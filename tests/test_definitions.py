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


@pytest.fixture(params=["internal", "external"], scope="module")
def validator(request):
    if request.param == "internal":
        yield ForisValidator(["tests/schemas/modules/definitions/"]), "definitions"
    elif request.param == "external":
        yield ForisValidator(
            ["tests/schemas/modules/definitions-external/"],
            ["tests/schemas/definitions/definitions-external/"]
        ), "definitions-external"


def test_valid(validator):
    validator, module_name = validator
    msg = {
        'kind': 'request',
        'module': module_name,
        'action': 'get',
        'data': {
            'object1': {'substring': 'bbbcc'},
            'string1': "aaa"
        }
    }
    validator.validate(msg)


def test_wrong_pattern(validator):
    validator, module_name = validator
    msg1 = {
        'kind': 'request',
        'module': module_name,
        'action': 'get',
        'data': {
            'object1': {'substring': 'Bbbcc'},
            'string1': "aaa"
        }
    }
    with pytest.raises(ValidationError):
        validator.validate(msg1)

    msg2 = {
        'kind': 'request',
        'module': module_name,
        'action': 'get',
        'data': {
            'object1': {'substring': 'bbbcc'},
            'string1': "Aaa"
        }
    }
    with pytest.raises(ValidationError):
        validator.validate(msg2)


def test_extra(validator):
    validator, module_name = validator
    msg1 = {
        'kind': 'request',
        'module': module_name,
        'action': 'get',
        'data': {
            'object1': {'substring': 'bbbcc'},
            'string1': "aaa",
            'non-existing': "bbb",
        }
    }
    with pytest.raises(ValidationError):
        validator.validate(msg1)

    msg2 = {
        'kind': 'request',
        'module': module_name,
        'action': 'get',
        'data': {
            'object1': {'substring': 'bbbcc', 'non-existing': "bbb"},
            'string1': "aaa",
        }
    }
    with pytest.raises(ValidationError):
        validator.validate(msg2)


def test_missing(validator):
    validator, module_name = validator
    msg1 = {
        'kind': 'request',
        'module': module_name,
        'action': 'get',
        'data': {
            'object1': {'substring': 'bbbcc'},
        }
    }
    with pytest.raises(ValidationError):
        validator.validate(msg1)

    msg2 = {
        'kind': 'request',
        'module': module_name,
        'action': 'get',
        'data': {
            'object1': {},
            'string1': "aaa",
        }
    }
    with pytest.raises(ValidationError):
        validator.validate(msg2)


def test_override():
    validator = ForisValidator(
        ["tests/schemas/modules/no_override_definition/"],
        ["tests/schemas/definitions/override_definition/"],
    )
    assert validator.is_valid({
        "module": "override",
        "kind": "request",
        "action": "get",
        "data": {"msg": "AAAAAA"},
    })
    assert not validator.is_valid({
        "module": "override",
        "kind": "request",
        "action": "get",
        "data": {"msg": "aaaaaa"},
    })

    validator = ForisValidator(
        ["tests/schemas/modules/override_definition/"],
        ["tests/schemas/definitions/override_definition/"],
    )
    assert not validator.is_valid({
        "module": "override",
        "kind": "request",
        "action": "get",
        "data": {"msg": "AAAAAA"},
    })
    assert validator.is_valid({
        "module": "override",
        "kind": "request",
        "action": "get",
        "data": {"msg": "aaaaaa"},
    })


def test_two_modules_with_same_definition():
    validator = ForisValidator([
        "tests/schemas/modules/redefinition/redefinition1",
        "tests/schemas/modules/redefinition/redefinition2",
    ])
    assert not validator.is_valid({
        "module": "redefinition1",
        "kind": "request",
        "action": "get",
        "data": {"msg": "AAAAAA"},
    })
    assert validator.is_valid({
        "module": "redefinition1",
        "kind": "request",
        "action": "get",
        "data": {"msg": "aaaaaa"},
    })
    assert not validator.is_valid({
        "module": "redefinition2",
        "kind": "request",
        "action": "get",
        "data": {"msg": "aaaaaa"},
    })
    assert validator.is_valid({
        "module": "redefinition2",
        "kind": "request",
        "action": "get",
        "data": {"msg": "AAAAAA"},
    })
