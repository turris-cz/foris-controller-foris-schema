# foris-schema
# Copyright (C) 2017-2021 CZ.NIC, z.s.p.o. <http://www.nic.cz>
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

from foris_schema import ForisValidator
from foris_schema.validator import (
    SchemaErrorMutipleTypes,
    ModuleAlreadyLoaded,
    SchemaErrorDefinitionAlreadyUsed,
    ForisSchemaValidationError
)


def test_missing_properties():
    with pytest.raises(ForisSchemaValidationError):
        ForisValidator(["tests/schemas/modules/wrong_schema/properties/"])


def test_missing_mandatory():
    with pytest.raises(ForisSchemaValidationError):
        ForisValidator(["tests/schemas/modules/wrong_schema/mandatory/"])


def test_module_mismatched():
    with pytest.raises(ForisSchemaValidationError):
        ForisValidator(["tests/schemas/modules/wrong_schema/mismatched/"])


def test_already_loaded():
    with pytest.raises(ModuleAlreadyLoaded):
        ForisValidator([
            "tests/schemas/modules/wrong_schema/same1/",
            "tests/schemas/modules/wrong_schema/same2/",
        ])


def test_multiple_types():
    with pytest.raises(SchemaErrorMutipleTypes):
        ForisValidator(["tests/schemas/modules/wrong_schema/multiple/"])


def test_redefinition_two_externals():
    with pytest.raises(SchemaErrorDefinitionAlreadyUsed) as excinfo:
        ForisValidator(
            ["tests/schemas/modules/simple/", ],
            ["tests/schemas/definitions/redefinition/", ],
        )
        assert len(str(excinfo.value)) < 256


@pytest.mark.parametrize(
    'schema, exception, err_type', [
        (["tests/schemas/modules/wrong_schema/properties/"], ForisSchemaValidationError, "ValidationError"),
        (
            [
                "tests/schemas/modules/wrong_schema/same1/",
                "tests/schemas/modules/wrong_schema/same2/",
            ], ModuleAlreadyLoaded, 'ModuleAlreadyLoaded'),
        (["tests/schemas/modules/wrong_schema/multiple/"],SchemaErrorMutipleTypes, 'SchemaErrorMutipleTypes'),
        (["tests/schemas/modules/wrong_schema/invalid_json/"], ForisSchemaValidationError, "JSONDecodeError")
    ]
)
def test_error_msg_brief(schema, exception, err_type):
    with pytest.raises(exception) as excinfo:
        ForisValidator(schema)
    assert err_type in str(excinfo)
