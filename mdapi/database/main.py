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
import re
import shutil
import tarfile
import tempfile
import time
from xml.etree import ElementTree

import pyzstd
import requests
from fedora_messaging.api import publish
from fedora_messaging.exceptions import ConnectionException, PublishReturned
from mdapi_messages.messages import RepoUpdateV1

from mdapi.confdata import servlogr, standard
from mdapi.database.base import compare_databases, index_database


def list_branches(status="current"):
    """
    As of 03rd September 2024,
    list_branches("current") returns ['epel10', 'epel8', 'epel9', 'epel9-next', 'f39', 'f40']
    list_branches("pending") returns ['eln', 'rawhide']
    list_branches("frozen")  returns ['f41']
    """
    urlx = f"{standard.BODHI_URL}/releases/"
    resp = requests.get(urlx, params={"state": status})  # noqa : S113
    resp.raise_for_status()
    data = [
        item["branch"]
        for item in resp.json()["releases"]
        if item["id_prefix"] in ("FEDORA", "FEDORA-EPEL", "FEDORA-EPEL-NEXT")
    ]
    data.sort()
    servlogr.logrobjc.info("Branches metadata acquired.")
    return data


def fetch_database(name, repmdurl, location):
    servlogr.logrobjc.info(f"[{name}] Downloading file {repmdurl} to {location}")
    resp = requests.get(repmdurl, verify=True)  # noqa : S113
    resp.raise_for_status()
    with open(location, "wb") as filestrm:
        filestrm.write(resp.content)


def extract_database(name, arcvname, location):
    servlogr.logrobjc.info(f"[{name}] Extracting {arcvname} to {location}")
    if arcvname.endswith(".xz"):
        with lzma.open(arcvname) as inp, open(location, "wb") as otptfile:
            otptfile.write(inp.read())
    elif arcvname.endswith(".tar.gz"):
        with tarfile.open(arcvname) as tararchv:
            tararchv.extractall(path=location, filter="data")
    elif arcvname.endswith(".gz"):
        with gzip.open(arcvname, "rb") as inp, open(location, "wb") as otptfile:
            otptfile.write(inp.read())
    elif arcvname.endswith(".bz2"):
        with bz2.open(arcvname) as inp, open(location, "wb") as otptfile:
            otptfile.write(inp.read())
    elif arcvname.endswith(".zst"):
        with open(arcvname, "rb") as inp, open(location, "wb") as otptfile:
            pyzstd.decompress_stream(inp, otptfile)
    else:
        servlogr.logrobjc.error(f"Could not extract {arcvname}")
        raise NotImplementedError(arcvname)


def publish_changes(name, packages, repmdurl):
    servlogr.logrobjc.info(f"[{name}] Publishing differences to Fedora Messaging bus")

    modified = bool(packages)
    if not modified:
        servlogr.logrobjc.warning(f"[{name}] No real changes detected - Skipping publishing on Fedora Messaging bus")  # noqa : E501
        return

    # Just publish the suffix of the URL.  The prefix is dl.fedoraproject.org
    # for lots of these, but we don't want to encourage people to download from
    # there.  It is the master mirror.  We want people to use
    # download.fedoraproject.org.. so, just obscure *exactly* which repo we're
    # talking about.

    urlx = "/".join(repmdurl.split("/")[4:])
    servlogr.logrobjc.info(f"[{name}] URL {urlx}")

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
        servlogr.logrobjc.error(f"Fedora Messaging broker rejected message {mesgobjc.id} - {excp}")
    except ConnectionException as excp:
        servlogr.logrobjc.error(f"Error occurred while sending message {mesgobjc.id} - {excp}")


def install_database(name, srce, dest):
    servlogr.logrobjc.info(f"[{name}] Installing {srce} to {dest}")
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
    repmdurl = f"{urlx}/repomd.xml"
    response = requests.get(repmdurl, verify=True)  # noqa : S113
    if not response:
        servlogr.logrobjc.error(f"[{name}] Failed to obtain {repmdurl} - {response}")
        return

    # Parse the XML document and get a list of locations and their SHAsum
    filelist = (
        (
            node.find("repo:location", standard.repomd_xml_namespace),
            node.find("repo:open-checksum", standard.repomd_xml_namespace),
        )
        for node in ElementTree.fromstring(response.text)  # noqa : S314
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
        servlogr.logrobjc.warning(f"No SQLite database could be found in {urlx}")

    for filename, hashdata, hashtype in filelist:
        repmdurl = f"{urlx}/{filename}"

        # First, determine if the file has changed by comparing hash
        database = None
        if "primary.sqlite" in filename:
            database = f"mdapi-{name}-primary.sqlite"
        elif "filelists.sqlite" in filename:
            database = f"mdapi-{name}-filelists.sqlite"
        elif "other.sqlite" in filename:
            database = f"mdapi-{name}-other.sqlite"

        # Have we downloaded this before?
        # Did it change?
        destfile = os.path.join(standard.DB_FOLDER, database)
        if not needs_update(destfile, hashdata, hashtype):
            servlogr.logrobjc.info(f"[{name}] No change detected from {repmdurl}")
            continue

        # Creating temporary directories with formatted names to remove them later easily, if needed
        tempargs = dict(prefix="mdapi-tempdrct-", dir=standard.DB_FOLDER)

        # If it has changed, then download it and move it into place
        with tempfile.TemporaryDirectory(**tempargs) as workdrct:
            tempdtbs = os.path.join(workdrct, database)
            archname = os.path.join(workdrct, filename)
            fetch_database(name, repmdurl, archname)
            extract_database(name, archname, tempdtbs)
            index_database(name, tempdtbs)
            if standard.PUBLISH_CHANGES:
                packages = compare_databases(name, tempdtbs, destfile, cacA, cacB).main()
                publish_changes(name, packages, repmdurl)
            else:
                servlogr.logrobjc.warning(f"[{name}] Not publishing to Fedora Messaging bus - Not comparing databases")  # noqa : E501
            install_database(name, tempdtbs, destfile)


def index_repositories():
    repolist = []

    # Obtain the development repos (rawhide + eventually Fn+1 branched)
    for rels in ["rawhide", *list_branches("frozen")]:
        if re.search(r"f\d+", rels):
            versdata = re.search(r"\d+", rels).group()
        elif rels == "rawhide":
            versdata = "rawhide"
        urlx = f"{standard.DL_SERVER}/pub/fedora/linux/development/{versdata}/Everything/x86_64/os/repodata/"  # noqa : E501
        servlogr.logrobjc.info(f"Acquired repo for {rels}/{versdata} branch at {urlx}")  # noqa : E501
        repolist.append((urlx, rels))
        urlx = urlx.replace("/x86_64/os/", "/source/tree/")
        repolist.append((urlx, f"src_{rels}"))

    urls = {
        "Fedora Linux": [
            "{dlserver}/pub/fedora/linux/releases/{versname}/Everything/x86_64/os/repodata/",
            "{dlserver}/pub/fedora/linux/updates/{versname}/Everything/x86_64/repodata/",
            "{dlserver}/pub/fedora/linux/updates/testing/{versname}/Everything/x86_64/repodata/",
        ],
        "Fedora EPEL": [
            "{dlserver}/pub/epel/{versname}/Everything/x86_64/repodata/",
            "{dlserver}/pub/epel/testing/{versname}/Everything/x86_64/repodata/",
        ],
        "Fedora EPEL Next": [
            "{dlserver}/pub/epel/next/{versname}/Everything/x86_64/repodata/",
            "{dlserver}/pub/epel/next/testing/{versname}/Everything/x86_64/repodata/",
        ],
    }

    repodict = {
        "fedora": ["{rlid}", "{rlid}-updates", "{rlid}-updates-testing"],
        "epel": ["{rlid}", "{rlid}-testing"],
        "epel-next": ["{rlid}", "{rlid}-testing"],
    }

    # Obtain the stable repos
    for rels in list_branches(status="current"):
        versdata = re.search(r"\d+(?:\.\d+)?", rels).group()
        linklist, idenlist = [], []

        if re.search(r"f\d+", rels):
            linklist, idenlist = urls["Fedora Linux"], repodict["fedora"]
        elif re.search(r"epel\d+(?:\.\d+)?", rels):
            linklist, idenlist = urls["Fedora EPEL"], repodict["epel"]
        elif re.search(r"epel\d-next", rels):
            linklist, idenlist = urls["Fedora EPEL Next"], repodict["epel-next"]

        for jndx, urli in enumerate(linklist):
            name = idenlist[jndx].format(rlid = rels)
            rurl = urli.format(dlserver=standard.DL_SERVER, versname=versdata)
            repolist.append((rurl, name))
            rurl = rurl.replace("/x86_64/os", "/source/tree")
            repolist.append((rurl, f"src_{name}"))

    # Finish with the koji repo
    repolist.append((f"{standard.KOJI_REPO}/rawhide/latest/x86_64/repodata/", "koji"))

    # In serial
    for repo in repolist:
        loop = True
        qant = 0
        while loop:
            qant += 1
            try:
                process_repo(repo)
                loop = False
            except OSError:
                if qant == 4:
                    raise
                # Most often due to an invalid stream, so let us try again
                time.sleep(standard.CRON_SLEEP)
                process_repo(repo)
