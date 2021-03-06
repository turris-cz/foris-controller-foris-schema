#!/usr/bin/env python
#
# Copyright (C) 2017-2020 CZ.NIC, z.s.p.o. (http://www.nic.cz/)
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

import os

from setuptools import setup


def get_version():
    with open(os.path.join(os.path.dirname(__file__), "foris_schema", "__init__.py")) as f:
        for line in f.readlines():
            if line.startswith("__version__ = "):
                return line.strip().lstrip('__version__ = "').rstrip('"')


DESCRIPTION = """
Library which validates whether the json matches
the protocol use between Foris web and a configuration backend.
"""

setup(
    name='foris-schema',
    version=get_version(),
    author='CZ.NIC, z.s.p.o. (http://www.nic.cz/)',
    author_email='packaging@turris.cz',
    packages=[
        'foris_schema',
        'foris_schema.cli'
    ],
    scripts=[],
    url='https://gitlab.nic.cz/turris/foris-controller/foris-schema',
    license='COPYING',
    description=DESCRIPTION,
    long_description=open('README.md').read(),
    install_requires=[
        'jsonschema',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest', 'pytest-cov',
    ],
    entry_points={
        'console_scripts': ['foris-schema=foris_schema.cli.__main__:main']
    }
)
