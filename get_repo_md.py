#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Copyright © 2015  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions
# of the GNU General Public License v.2, or (at your option) any later
# version.  This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY expressed or implied, including the
# implied warranties of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.  You
# should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Any Red Hat trademarks that are incorporated in the source
# code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission
# of Red Hat, Inc.
#

'''
This script is meant to be run in a cron job or triggered job and will pull
the sqlite database present in the repodata folder of all active Fedora
branches.

Active Fedora branches are retrieved from pkgdb2:
    https://admin.fedoraproject.org/pkgdb/

sqlite database are retrieved from the master Fedora mirror:
    http://dl.fedoraproject.org/pub/fedora/linux/

'''

import argparse
import contextlib
import itertools
import multiprocessing
import os
import shutil
import tempfile

import requests

KOJI_REPO = 'https://kojipkgs.fedoraproject.org/repos/'
PKGDB2_URL = 'https://admin.fedoraproject.org/pkgdb/'


def list_branches(status='Active'):
    ''' Return the list of Fedora branches corresponding to the given
    status.
    '''
    url = PKGDB2_URL + 'api/collections?clt_status=%s' % status
    req = requests.get(url)
    data = req.json()
    return data['collections']


def decompress_primary_db(archive, location):
    ''' Decompress the given XZ archive at the specified location. '''
    if archive.endswith('.xz'):
        import lzma
        with contextlib.closing(lzma.LZMAFile(archive)) as stream_xz:
            data = stream_xz.read()
        with open(location, 'wb') as stream:
            stream.write(data)
    elif archive.endswith('.gz'):
        import tarfile
        with tarfile.open(archive) as tar:
            tar.extractall(path=location)
    elif archive.endswith('.bz2'):
        import bz2
        with open(location, 'wb') as out:
            bzar = bz2.BZ2File(archive)
            out.write(bzar.read())
            bzar.close()
    elif archive.endswith('.sqlite'):
        with open(location, 'wb') as out:
            with open(archive) as inp:
                out.write(inp.read())


def process_repo(tupl):
    ''' Retrieve the repo metadata at the given url and store them using
    the provided name.
    '''
    destfolder, repo = tupl
    url, name = repo
    repomd_url = url + '/repomd.xml'
    req = requests.get(repomd_url)
    files = []
    for row in req.text.split('\n'):
        if '.sqlite' in row:
            files.append(row.split('"')[1].replace('repodata/', ''))

    working_dir = tempfile.mkdtemp(prefix='mdapi-')
    for filename in files:
        repomd_url = url + '/' + filename
        print('%s - Download file: %s' % (name.ljust(10), repomd_url))
        req = requests.get(repomd_url)
        archive = os.path.join(working_dir, filename)
        with open(archive, 'wb') as stream:
            stream.write(req.content)
        db = None
        if 'primary.sqlite' in filename:
            db = 'mdapi-%s-primary.sqlite' % name
        elif 'filelists.sqlite' in filename:
            db = 'mdapi-%s-filelists.sqlite' % name
        elif 'other.sqlite' in filename:
            db = 'mdapi-%s-other.sqlite' % name

        destfile = os.path.join(destfolder, db)
        decompress_primary_db(archive, destfile)

    shutil.rmtree(working_dir)


def main():
    ''' Get the repo metadata. '''
    parser = argparse.ArgumentParser(prog="get_repo_md")
    # General connection options
    parser.add_argument('config', help="Configuration file to use")
    args = parser.parse_args()

    # Load the configuration file
    CONFIG = {}
    configfile = args.config
    with open(configfile) as config_file:
        exec(compile(
            config_file.read(), configfile, 'exec'), CONFIG)

    if not os.path.exists(CONFIG['DB_FOLDER']):
        print('Could not find the configuration file')
        return 1

    repositories = []
    # Get the koji repo
    repositories.append(
        (KOJI_REPO + 'rawhide/latest/x86_64/repodata', 'koji')
    )
    # Get the development repos (rawhide + eventually Fn+1 branched)
    dev_releases = list_branches(status='Under Development')
    for release in dev_releases:
        if release['status'] != 'Under Development':
            continue
        version = release['version']
        if version == 'devel':
            version = 'rawhide'
        url = 'http://dl.fedoraproject.org/pub/fedora/linux/' \
            'development/%s/x86_64/os/repodata' % version
        repositories.append(
            (url, release['koji_name'])
        )

    stable_releases = list_branches(status='Active')
    for release in stable_releases:
        if release['status'] != 'Active':
            continue
        version = release['version']
        url = 'http://dl.fedoraproject.org/pub/fedora/linux/' \
            'releases/%s/x86_64/repodata' % version
        repositories.append((url, release['koji_name']))

        url = 'http://dl.fedoraproject.org/pub/fedora/linux/' \
            'updates/%s/x86_64/repodata' % version
        repositories.append((url, release['koji_name'] + '-updates'))

        url = 'http://dl.fedoraproject.org/pub/fedora/linux/' \
            'updates/testing/%s/x86_64/repodata' % version
        repositories.append((url, release['koji_name'] + '-updates-testing'))

    p = multiprocessing.Pool(10)
    p.map(process_repo, itertools.product([CONFIG['DB_FOLDER']], repositories))

    return 0


if __name__ == '__main__':
    main()
