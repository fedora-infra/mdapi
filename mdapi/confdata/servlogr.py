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

import logging

"""
TODO:
Scope of the logging object needs to be reworked for the logs produced by the functions present
in the "appviews" module
"""

"""
logging.basicConfig(
    format="%(asctime)s\t%(levelname)s\t%(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
)
"""

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="[%Y-%m-%d %I:%M:%S %z]",
    level=logging.INFO,
)

logrobjc = logging.getLogger(__name__)
