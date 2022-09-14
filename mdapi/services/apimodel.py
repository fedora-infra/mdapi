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

from dataclasses import dataclass


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
            "arch": self.arch,
            "epoch": self.epoch,
            "version": self.version,
            "release": self.release,
            "summary": self.summary,
            "description": self.description,
            "basename": self.basename,
            "url": self.url,
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
            "name": self.name,
            "epoch": self.epoch,
            "version": self.version,
            "release": self.release,
            "flags": self.flags,
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
            "dirname": self.dirname,
            "filenames": self.filenames,
            "filetypes": self.filetypes,
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
            "author": self.author,
            "changelog": self.changelog,
            "date": self.date,
        }
        return changelog
