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

"""
Queries used by the database populating backend
"""

INDEX_DATABASE = "CREATE INDEX packageSource ON packages (rpm_sourcerpm)"

OBTAIN_TABLE_NAMES = "SELECT name FROM sqlite_master WHERE type='table'"

RELATIONS_QUERY = """
    SELECT
        {table}.name,
        {table}.flags,
        {table}.epoch,
        {table}.version,
        {table}.release,
        packages.name
    FROM {table}, packages
    WHERE {table}.pkgKey == packages.pkgKey;
"""

FILES_QUERY = """
    SELECT
        {table}.name,
        {table}.type,
        packages.name
    FROM {table}, packages
    WHERE {table}.pkgKey == packages.pkgKey;
"""

PACKAGES_CACHE_BUILDER = """
    SELECT
        {table}.pkgId,
        {table}.name
    FROM {table};
"""

PACKAGES_QUERY = """
    SELECT
        {table}.name,
        {table}.version,
        {table}.release,
        {table}.epoch,
        {table}.arch
    FROM {table};
"""

CHANGELOG_QUERY = """
    SELECT
        packages.pkgId,
        {table}.author,
        {table}.date,
        {table}.changelog
    FROM {table}, packages
    WHERE {table}.pkgKey == packages.pkgKey;
"""

FILELIST_QUERY = """
    SELECT
        packages.pkgId,
        {table}.dirname,
        {table}.filenames,
        {table}.filetypes
    FROM {table}, packages
    WHERE {table}.pkgKey == packages.pkgKey;
"""

DEFAULT_QUERY = "SELECT * from {table};"

queries = {
    "conflicts": RELATIONS_QUERY,
    "enhances": RELATIONS_QUERY,
    "obsoletes": RELATIONS_QUERY,
    "provides": RELATIONS_QUERY,
    "requires": RELATIONS_QUERY,
    "supplements": RELATIONS_QUERY,
    "recommends": RELATIONS_QUERY,
    "suggests": RELATIONS_QUERY,
    "files": FILES_QUERY,
    "packages": PACKAGES_QUERY,
    "changelog": CHANGELOG_QUERY,
    "filelist": FILELIST_QUERY,
}

"""
Queries used by the mdapi web service
"""

GET_PACKAGE = """
    SELECT
        pkgKey,
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
    ORDER BY epoch DESC, version DESC, release DESC
"""

GET_PACKAGE_INFO = """
    SELECT
        rowid,
        pkgKey,
        name,
        epoch,
        version,
        release,
        flags
    FROM {}
    WHERE pkgKey = ?
"""

GET_CO_PACKAGE = """
    SELECT DISTINCT(name)
    FROM packages
    WHERE rpm_sourcerpm = ?
"""

GET_PACKAGE_BY_SRC = """
    SELECT
        pkgKey,
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
    ORDER BY epoch DESC, version DESC, release DESC
"""

GET_PACKAGE_BY = """
    SELECT
        p.pkgKey,
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
    ORDER BY p.epoch DESC, p.version DESC, p.release DESC
"""

GET_FILES = """
    SELECT
        f.pkgKey,
        f.dirname,
        f.filenames,
        f.filetypes
    FROM filelist f
    JOIN packages p ON p.pkgId = ?
    WHERE f.pkgKey = p.pkgKey
    ORDER BY f.filenames
"""

GET_CHANGELOGS = """
    SELECT
        c.pkgKey,
        c.author,
        c.changelog,
        c.date
    FROM changelog c
    JOIN packages p ON p.pkgId = ?
    WHERE c.pkgKey = p.pkgKey
    ORDER BY c.date DESC
"""
