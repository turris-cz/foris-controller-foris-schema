#!/usr/bin/env python
#
# Copyright (C) 2017 CZ.NIC, z.s.p.o. (http://www.nic.cz/)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#

from setuptools import setup
from foris_schema import __version__

DESCRIPTION = """
Library which validates whether the json matches
the protocol use between Foris web and a configuration backend.
"""

setup(
    name='foris-schema',
    version=__version__,
    author='CZ.NIC, z.s.p.o. (http://www.nic.cz/)',
    author_email='stepan.henek@nic.cz',
    packages=['foris_schema', ],
    scripts=[],
    url='https://gitlab.labs.nic.cz/turris/foris-schema',
    license='COPYING',
    description=DESCRIPTION,
    long_description=open('README.rst').read(),
    requires=[
        'jsonschema',
    ],
    provides=[
        'foris_schema',
    ],
)
