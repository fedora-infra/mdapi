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
DB mapping for the filelists sqlite DB.
'''

import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base

BASE = declarative_base()

class Package(BASE):
    ''' Maps the packages table in the primary.sqlite database from
    repodata to a python object.
    '''
    __tablename__ = 'packages'
    pkgKey = sa.Column(sa.Integer, primary_key=True)
    pkgId = sa.Column(sa.Text)


class Filelist(BASE):
    ''' Maps the packages table in the filelists.sqlite database from
    repodata to a python object.
    '''
    __tablename__ = 'filelist'
    pkgKey = sa.Column(sa.Integer, primary_key=True)
    dirname = sa.Column(sa.Text, primary_key=True)
    filenames = sa.Column(sa.Text, primary_key=True)
    filetypes = sa.Column(sa.Text, primary_key=True)

    def to_json(self):
        filelist = {
            'dirname': self.dirname,
            'filenames': self.filenames,
            'filetypes': self.filetypes,
        }
        return filelist
