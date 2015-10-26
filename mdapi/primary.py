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
DB mapping for the primary sqlite DB.
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
    name = sa.Column(sa.Text)
    rpm_sourcerpm = sa.Column(sa.Text)
    version = sa.Column(sa.Text)
    epoch = sa.Column(sa.Text)
    release = sa.Column(sa.Text)
    arch = sa.Column(sa.Text)
    summary = sa.Column(sa.Text)
    description = sa.Column(sa.Text)

    @property
    def basename(self):
        ''' Return the base package name using the rpm_sourcerpms info. '''
        return self.rpm_sourcerpm.rsplit('-', 2)[0]

    def to_json(self):
        pkg = {
            'arch': self.arch,
            'epoch': self.epoch,
            'version': self.version,
            'release': self.release,
            'summary': self.summary,
            'description': self.description,
            'basename': self.basename,
        }
        return pkg
