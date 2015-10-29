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
MDAPI internal API to interact with the database.
'''

import contextlib
import time

import sqlalchemy as sa

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.exc import SQLAlchemyError

import mdapi.changelog as changelog
import mdapi.filelist as filelist
import mdapi.primary as primary

RETRY_ATTEMPT = 3


def create_session(db_url, debug=False, pool_recycle=3600):
    """ Create the Session object to use to query the database.

    :arg db_url: URL used to connect to the database. The URL contains
    information with regards to the database engine, the host to connect
    to, the user and password and the database name.
      ie: <engine>://<user>:<password>@<host>/<dbname>
    :kwarg debug: a boolean specifying wether we should have the verbose
        output of sqlalchemy or not.
    :return a Session that can be used to query the database.

    """
    engine = sa.create_engine(
        db_url, echo=debug, pool_recycle=pool_recycle)
    scopedsession = scoped_session(sessionmaker(bind=engine))
    return scopedsession


@contextlib.contextmanager
def session_manager(db_url, debug=False, pool_recycle=3600):
    """ A handy context manager for our sessions. """
    session = create_session(db_url, debug=debug, pool_recycle=pool_recycle)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_package(session, pkg_name):
    ''' Return information about a package, if we can find it.
    '''
    cnt = 0
    try:
        pkg = session.query(
            primary.Package
        ).filter(
            primary.Package.name == pkg_name
        )
        output = pkg.first()
    except SQLAlchemyError as err:
        cnt += 1
        if cnt > RETRY_ATTEMPT:
            raise
        else:
            time.sleep(0.1)
            output = get_package(session, pkg_name)

    return output


def get_co_packages(session, srcpkg_name):
    ''' Return the name of all the packages coming from the same
    source-package.
    '''
    cnt = 0
    try:
        pkg = session.query(
            primary.Package
        ).filter(
            primary.Package.rpm_sourcerpm == srcpkg_name
        )
        output = pkg.all()
    except SQLAlchemyError as err:
        cnt += 1
        if cnt > RETRY_ATTEMPT:
            raise
        else:
            time.sleep(0.1)
            output = get_co_packages(session, srcpkg_name)

    return output


def get_files(session, pkg_id):
    ''' Return the list of all the files in a package given its key.
    '''
    cnt = 0
    try:
        pkg = session.query(
            filelist.Filelist
        ).filter(
            filelist.Package.pkgId == pkg_id,
            filelist.Filelist.pkgKey == filelist.Package.pkgKey
        ).order_by(
            filelist.Filelist.filenames
        )
        output = pkg.all()
    except SQLAlchemyError as err:
        cnt += 1
        if cnt > RETRY_ATTEMPT:
            raise
        else:
            time.sleep(0.1)
            output = get_files(session, pkg_id)

    return output


def get_changelog(session, pkg_id):
    ''' Return the list of all the changelog in a package given its key.
    '''
    cnt = 0
    try:
        pkg = session.query(
            changelog.Changelog
        ).filter(
            changelog.Package.pkgId == pkg_id,
            changelog.Changelog.pkgKey == changelog.Package.pkgKey
        ).order_by(
            changelog.Changelog.date.desc()
        )
        output = pkg.all()
    except SQLAlchemyError as err:
        cnt += 1
        if cnt > RETRY_ATTEMPT:
            raise
        else:
            time.sleep(0.1)
            output = get_changelog(session, pkg_id)

    return output
