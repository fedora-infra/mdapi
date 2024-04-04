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

import sqlite3

from mdapi.confdata import servlogr
from mdapi.database.sqlq import DEFAULT_QUERY, INDEX_DATABASE, OBTAIN_TABLE_NAMES, queries


def index_database(name, tempdtbs):
    servlogr.logrobjc.info(f"[{name}] Indexing database {tempdtbs}")
    if tempdtbs.endswith("primary.sqlite"):
        # TODO: Try the "with sqlite3.connect(tempdtbs) as connobjc" statement here
        connobjc = sqlite3.connect(tempdtbs)
        connobjc.execute(INDEX_DATABASE)
        connobjc.commit()
        connobjc.close()


class compare_databases:
    def __init__(self, name, dbsA, dbsB, cacA, cacB):
        self.name = name
        self.dbsA = dbsA
        self.dbsB = dbsB
        self.cacA = cacA
        self.cacB = cacB

        # These two tables have a primary key reference to a table *in another
        # database*.  Consequently, we have to use an in-memory cache to do the
        # "join" ourselves.  Specifically, we need to swap out pkgId for pkgname.
        self.cache_dependent_tables = ["filelist", "changelog"]

        # This table produces the cache.
        self.cache_producing_tables = ["packages"]

        # Prune out some squirrelly tables we're not going to worry about.
        self.ignored_database_tables = [
            # The "packages" table in the "filelists" db is full of primary keys
            # and is prone to false positives.
            ("filelists", "packages"),
            # Same goes for the "packages" table in the "other" db.
            ("other", "packages"),
        ]

    def obtain_table_names(self, location):
        connobjc = sqlite3.connect(location)
        for name in connobjc.execute(OBTAIN_TABLE_NAMES):
            if name[0] == "db_info":
                continue
            yield name[0]
        connobjc.close()

    def change_row_to_package(self, rowe):
        if "/" in rowe[0]:
            name = rowe[-1]
        else:
            name = rowe[0]
        return name.split("(")[0]

    def obtain_all_rows(self, location, tableobj, cacheobj):
        connobjc = sqlite3.connect(location)
        sqlquery = queries.get(tableobj, DEFAULT_QUERY).format(table=tableobj)
        for indx, rowe in enumerate(connobjc.execute(sqlquery)):  # noqa : B007
            if tableobj in self.cache_dependent_tables:
                if rowe[0] in cacheobj:
                    yield (cacheobj[rowe[0]], *rowe[1:])
                else:
                    servlogr.logrobjc.debug(f"[{self.name}] {rowe[0]} does not appear in the {tableobj} cache for {location}")  # noqa : E501
                    servlogr.logrobjc.debug(f"[{self.name}] Dropping from comparison")
            else:
                yield rowe
        connobjc.close()

    def build_cache(self, location, tableobj, cacheobjc):
        connobjc = sqlite3.connect(location)
        sqlquery = queries.get(tableobj, DEFAULT_QUERY).format(table=tableobj)
        for pkgId, pkgname, *args in connobjc.execute(sqlquery):  # noqa : B007
            cacheobjc[pkgId] = pkgname
        connobjc.close()

    def should_compare(self, tableobj):
        for test, trgt in self.ignored_database_tables:
            if test in self.dbsA and tableobj == trgt:
                return False
        return True

    def main(self):
        servlogr.logrobjc.info(f"[{self.name}] Comparing {self.dbsA} against {self.dbsB}")

        tablistA = list(self.obtain_table_names(self.dbsA))
        tablistB = list(self.obtain_table_names(self.dbsB))

        if not tablistA and not tablistB:
            servlogr.logrobjc.error("Something is not right")
            raise RuntimeError("Something is not right")

        if not tablistB:
            # We have never downloaded this before...
            # so we have nothing to compare it against. Just return and say there
            # are "no differences".
            servlogr.logrobjc.warning(f"[{self.name}] Database empty - {self.dbsB} cannot compare")
            return set()

        if len(tablistA) != len(tablistB):
            raise ValueError("Cannot compare disparate databases")

        # These should be the same
        tblelist = tablistA

        tblelist = [tableobj for tableobj in tblelist if self.should_compare(tableobj)]

        # Compare the contents of both tables and return a list of changed packages
        rsltdata = set()
        for tableobj in tblelist:
            if tableobj in self.cache_producing_tables:
                self.build_cache(self.dbsA, tableobj, self.cacA)
                self.build_cache(self.dbsB, tableobj, self.cacB)
            rowlistA = set(self.obtain_all_rows(self.dbsA, tableobj, self.cacA))
            rowlistB = set(self.obtain_all_rows(self.dbsB, tableobj, self.cacB))
            modified = rowlistA.symmetric_difference(rowlistB)
            rsltdata.update({self.change_row_to_package(rowe) for rowe in modified})

        return rsltdata
