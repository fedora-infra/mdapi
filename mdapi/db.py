# -*- coding: utf-8 -*-
#
# Copyright © 2019  Red Hat, Inc.
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

from dataclasses import dataclass

GET_PACKAGE = """SELECT pkgKey,
                        pkgId,
                        name,
                        rpm_sourcerpm,
                        epoch,
                        version,
                        release,
                        arch,
                        summary,
                        description,
                        url
                 FROM packages
                 WHERE name = ?
                 ORDER BY epoch DESC, version DESC, release DESC"""

GET_PACKAGE_INFO = """SELECT rowid,
                             pkgKey,
                             name,
                             epoch,
                             version,
                             release,
                             flags
                      FROM {}
                      WHERE pkgKey = ?"""

GET_CO_PACKAGE = """SELECT DISTINCT(name)
                    FROM packages
                    WHERE rpm_sourcerpm = ?"""

GET_PACKAGE_BY_SRC = """SELECT pkgKey,
                               pkgId,
                               name,
                               rpm_sourcerpm,
                               epoch,
                               version,
                               release,
                               arch,
                               summary,
                               description,
                               url
                        FROM packages
                        WHERE rpm_sourcerpm LIKE ?
                        ORDER BY epoch DESC, version DESC, release DESC"""

GET_PACKAGE_BY = """SELECT p.pkgKey,
                           p.pkgId,
                           p.name,
                           p.rpm_sourcerpm,
                           p.epoch,
                           p.version,
                           p.release,
                           p.arch,
                           p.summary,
                           p.description,
                           p.url
                    FROM packages p
                    JOIN {} t ON t.pkgKey = p.pkgKey
                    WHERE t.name = ?
                    ORDER BY p.epoch DESC, p.version DESC, p.release DESC"""

GET_FILES = """SELECT f.pkgKey,
                      f.dirname,
                      f.filenames,
                      f.filetypes
               FROM filelist f
               JOIN packages p ON p.pkgId = ?
               WHERE f.pkgKey = p.pkgKey
               ORDER BY f.filenames"""


GET_CHANGELOGS = """SELECT c.pkgKey,
                           c.author,
                           c.changelog,
                           c.date
                    FROM changelog c
                    JOIN packages p ON p.pkgId = ?
                    WHERE c.pkgKey = p.pkgKey
                    ORDER BY c.date DESC"""


@dataclass
class Packages:
    pkgKey: int
    pkgId: str
    name: str
    rpm_sourcerpm: str
    epoch: str
    version: str
    release: str
    arch: str
    summary: str
    description: str
    url: str

    @property
    def basename(self):
        return self.rpm_sourcerpm.rsplit("-", 2)[0]

    def to_json(self):
        pkg = {
            'arch': self.arch,
            'epoch': self.epoch,
            'version': self.version,
            'release': self.release,
            'summary': self.summary,
            'description': self.description,
            'basename': self.basename,
            'url': self.url,
        }
        return pkg


@dataclass
class Dependencies:
    rowid: int
    pkgKey: int
    name: str
    epoch: str
    version: str
    release: str
    flags: str

    def to_json(self):
        pkg = {
            'name': self.name,
            'epoch': self.epoch,
            'version': self.version,
            'release': self.release,
            'flags': self.flags,
        }
        return pkg


@dataclass
class FileList:
    pkgKey: int
    dirname: str
    filenames: str
    filetypes: str

    def to_json(self):
        filelist = {
            'dirname': self.dirname,
            'filenames': self.filenames,
            'filetypes': self.filetypes,
        }
        return filelist


@dataclass
class ChangeLog:
    pkgKey: int
    author: str
    changelog: str
    date: int

    def to_json(self):
        changelog = {
                'author': self.author,
                'changelog': self.changelog,
                'date': self.date,
        }
        return changelog
