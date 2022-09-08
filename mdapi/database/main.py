"""
mdapi
Copyright (C) 2015-2022 Red Hat, Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Any Red Hat trademarks that are incorporated in the source
code or documentation are not subject to the GNU General Public
License and may only be used or replicated with the express permission
of Red Hat, Inc.
"""

import bz2
import gzip
import hashlib
import lzma
import os.path
import shutil
import tarfile
import tempfile
from xml.etree import ElementTree

import requests
from fedora_messaging.api import publish
from fedora_messaging.exceptions import ConnectionException, PublishReturned
from mdapi_messages.messages import RepoUpdateV1

from mdapi.confdata.servlogr import logrobjc
from mdapi.confdata.standard import (
    DB_FOLDER,
    DL_VERIFY,
    PKGDB2_URL,
    PKGDB2_VERIFY,
    PUBLISH_CHANGES,
    repomd_xml_namespace,
)
from mdapi.database.base import compare_databases, index_database


def list_branches(status="Active"):
    urlx = "%s/api/collections?clt_status=%s" % (PKGDB2_URL, status)
    resp = requests.get(urlx, verify=PKGDB2_VERIFY)
    resp.raise_for_status()
    data = resp.json()
    logrobjc.info("Branches metadata acquired.")
    return data["collections"]


def fetch_database(name, repmdurl, location):
    logrobjc.info("[%s] Downloading file %s to %s" % (name, repmdurl, location))
    resp = requests.get(repmdurl, verify=DL_VERIFY)
    resp.raise_for_status()
    with open(location, "wb") as filestrm:
        filestrm.write(resp.content)


def extract_database(name, arcvname, location):
    logrobjc.info("[%s] Extracting %s to %s" % (name, arcvname, location))
    if arcvname.endswith(".xz"):
        with lzma.open(arcvname) as inp, open(location, "wb") as otptfile:
            otptfile.write(inp.read())
    elif arcvname.endswith(".tar.gz"):
        with tarfile.open(arcvname) as tararchv:
            tararchv.extractall(path=location)
    elif arcvname.endswith(".gz"):
        with gzip.open(arcvname, "rb") as inp, open(location, "wb") as otptfile:
            otptfile.write(inp.read())
    elif arcvname.endswith(".bz2"):
        with bz2.open(arcvname) as inp, open(location, "wb") as otptfile:
            otptfile.write(inp.read())
    else:
        logrobjc.error("Could not extract %s" % (arcvname))
        raise NotImplementedError(arcvname)


def publish_changes(name, packages, repmdurl):
    logrobjc.info("[%s] Publishing differences to Fedora Messaging bus" % (name))

    modified = bool(packages)
    if not modified:
        logrobjc.warning(
            "[%s] No real changes detected - Skipping publishing on Fedora Messaging bus"
        )
        return

    # Just publish the suffix of the URL.  The prefix is dl.fedoraproject.org
    # for lots of these, but we don't want to encourage people to download from
    # there.  It is the master mirror.  We want people to use
    # download.fedoraproject.org.. so, just obscure *exactly* which repo we're
    # talking about.

    urlx = "/".join(repmdurl.split("/")[4:])
    logrobjc.info("[%s] URL %s" % (name, urlx))

    mesgobjc = RepoUpdateV1(
        body=dict(
            name=name,
            packages=list(packages),
            url=urlx,
        )
    )

    try:
        publish(mesgobjc)
    except PublishReturned as excp:
        logrobjc.error("Fedora Messaging broker rejected message %s - %s" % (mesgobjc.id, excp))
    except ConnectionException as excp:
        logrobjc.error("Error occurred while sending message %s - %s" % (mesgobjc.id, excp))


def install_database(name, srce, dest):
    logrobjc.info("[%s] Installing %s to %s" % (name, srce, dest))
    shutil.move(srce, dest)


def needs_update(loclfile, srcehash, hashtype):
    """
    Compare SHA of the local and remote file
    Return True if our local file needs to be updated
    """
    if not os.path.isfile(loclfile):
        # If we have never downloaded the archives before,
        # then obviously it has "changed"...
        return True

    # Old EPEL5 does not even know which version of SHA it is using...
    if hashtype == "sha":
        hashtype = "sha1"

    hashdata = getattr(hashlib, hashtype)()
    with open(loclfile, "rb") as fileobjc:
        hashdata.update(fileobjc.read())
    loclhash = hashdata.hexdigest()
    if loclhash != srcehash:
        return True
    return False


def process_repo(repo):
    """
    Retrieve the repo metadata at the given URL and store them using the provided name.
    """
    urlx, name = repo
    repmdurl = "%s/repomd.xml" % urlx
    response = requests.get(repmdurl, verify=DL_VERIFY)
    if not response:
        logrobjc.error("[%s] Failed to obtain %s - %s" % (name, repmdurl, response))
        return

    # Parse the XML document and get a list of locations and their SHAsum
    filelist = (
        (
            node.find("repo:location", repomd_xml_namespace),
            node.find("repo:open-checksum", repomd_xml_namespace),
        )
        for node in ElementTree.fromstring(response.text)
    )

    # Extract out the attributes that we are really interested in
    filelist = (
        (fobj.attrib["href"].replace("repodata/", ""), sobj.text, sobj.attrib["type"])
        for fobj, sobj in filelist
        if fobj is not None and sobj is not None
    )

    # Filter down to only SQLite3 databases
    filelist = ((fobj, sobj, tobj) for fobj, sobj, tobj in filelist if ".sqlite" in fobj)

    # We need to ensure the primary database comes first, so we can build a PKEY cache
    prmyfrst = lambda item: "primary" not in item[0]  # noqa
    filelist = sorted(filelist, key=prmyfrst)

    # Primary key caches built from the primary databases, so we can make sense
    # of the contents of the filelist and changelog databases.
    cacA, cacB = {}, {}

    if not filelist:
        logrobjc.warning("No SQLite database could be found in %s" % (urlx))

    for filename, hashdata, hashtype in filelist:
        repmdurl = "%s/%s" % (urlx, filename)

        # First, determine if the file has changed by comparing hash
        database = None
        if "primary.sqlite" in filename:
            database = "mdapi-%s-primary.sqlite" % name
        elif "filelists.sqlite" in filename:
            database = "mdapi-%s-filelists.sqlite" % name
        elif "other.sqlite" in filename:
            database = "mdapi-%s-other.sqlite" % name

        # Have we downloaded this before?
        # Did it change?
        destfile = os.path.join(DB_FOLDER, database)
        if not needs_update(destfile, hashdata, hashtype):
            logrobjc.info("[%s] No change detected from %s" % (name, repmdurl))
            continue

        # If it has changed, then download it and move it into place
        tempargs = dict(prefix="mdapi", dir="/var/tmp")
        with tempfile.TemporaryDirectory(**tempargs) as workdrct:
            tempdtbs = os.path.join(workdrct, database)
            archname = os.path.join(workdrct, filename)
            fetch_database(name, repmdurl, archname)
            extract_database(name, archname, tempdtbs)
            index_database(name, tempdtbs)
            if PUBLISH_CHANGES:
                packages = compare_databases(name, tempdtbs, destfile, cacA, cacB).main()
                publish_changes(name, packages, repmdurl)
            else:
                logrobjc.warning(
                    "[%s] Not publishing to Fedora Messaging bus - Not comparing databases" % (name)
                )
            install_database(name, tempdtbs, destfile)
