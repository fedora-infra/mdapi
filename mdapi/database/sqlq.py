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
