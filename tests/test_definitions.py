# foris-schema
# Copyright (C) 2017 CZ.NIC, z.s.p.o. <http://www.nic.cz>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pytest

from jsonschema import ValidationError

from foris_schema import ForisValidator


@pytest.fixture(scope="module")
def validator():
    return ForisValidator(["tests/schemas/definitions/"])


def test_valid(validator):
    msg = {
        'kind': 'request',
        'module': 'definitions',
        'action': 'get',
        'data': {
            'object1':{'substring': 'bbbcc'},
            'string1': "aaa"
        }
    }
    validator.validate(msg)
    validator.validate_verbose(msg)


def test_wrong_pattern(validator):
    msg1 = {
        'kind': 'request',
        'module': 'definitions',
        'action': 'get',
        'data': {
            'object1':{'substring': 'Bbbcc'},
            'string1': "aaa"
        }
    }
    with pytest.raises(ValidationError):
        validator.validate(msg1)
    with pytest.raises(ValidationError):
        validator.validate_verbose(msg1)

    msg2 = {
        'kind': 'request',
        'module': 'definitions',
        'action': 'get',
        'data': {
            'object1':{'substring': 'bbbcc'},
            'string1': "Aaa"
        }
    }
    with pytest.raises(ValidationError):
        validator.validate(msg2)
    with pytest.raises(ValidationError):
        validator.validate_verbose(msg2)


def test_extra(validator):
    msg1 = {
        'kind': 'request',
        'module': 'definitions',
        'action': 'get',
        'data': {
            'object1':{'substring': 'bbbcc'},
            'string1': "aaa",
            'non-existing': "bbb",
        }
    }
    with pytest.raises(ValidationError):
        validator.validate(msg1)
    with pytest.raises(ValidationError):
        validator.validate_verbose(msg1)

    msg2 = {
        'kind': 'request',
        'module': 'definitions',
        'action': 'get',
        'data': {
            'object1':{'substring': 'bbbcc', 'non-existing': "bbb"},
            'string1': "aaa",
        }
    }
    with pytest.raises(ValidationError):
        validator.validate(msg2)
    with pytest.raises(ValidationError):
        validator.validate_verbose(msg2)


def test_missing(validator):
    msg1 = {
        'kind': 'request',
        'module': 'definitions',
        'action': 'get',
        'data': {
            'object1':{'substring': 'bbbcc'},
        }
    }
    with pytest.raises(ValidationError):
        validator.validate(msg1)
    with pytest.raises(ValidationError):
        validator.validate_verbose(msg1)

    msg2 ={
        'kind': 'request',
        'module': 'definitions',
        'action': 'get',
        'data': {
            'object1':{},
            'string1': "aaa",
        }
    }
    with pytest.raises(ValidationError):
        validator.validate(msg2)
    with pytest.raises(ValidationError):
        validator.validate_verbose(msg2)
