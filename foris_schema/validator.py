# foris-schema
# Copyright (C) 2018-2021 CZ.NIC, z.s.p.o. <http://www.nic.cz>
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

import copy
import json
import os

from json.decoder import JSONDecodeError

from jsonschema import validate as schema_validate, Draft4Validator, ValidationError
from .custom_format_checkers import format_checker


BASE_SCHEMA = {
    "$schema": "http://turris.cz/foris-schema-base#",
    "type": "object",
    "properties": {
        "kind": {"enum": ["request", "reply", "notification"]},
        "module": {"enum": []},  # modules will be filled later
        "action": {"type": "string"},
        "data": {"type": "object"},
        "errors": {"type": "array"},
    },
    "required": ["kind", "module", "action"],
    "additionalProperties": False,
}

ERROR_SCHEMA = {
    "$schema": "http://turris.cz/foris-schema-error#",
    "type": "object",
    "properties": {
        "errors": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "stacktrace": {"type": "string"}
                },
                "additionalProperties": False,
                "required": ["description", "stacktrace"],
            },
            "minItems": 1,
        },
    },
    "required": ["errors"],
}


SCHEMA_FOR_SCHEMAS = {
    "type": "object",
    "properties": {
        "definitions": {"type": "object"},
        "$schema": {"type": "string"},
        "oneOf": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "properties": {
                        "type": "object",
                        "properties": {
                            "module": {
                                "type": "object",
                                "properties": {
                                    "enum": {
                                        "type": "array",
                                        "items": {"enum": []},  # insert name of the module
                                        "minItems": 1,
                                        "maxItems": 1,
                                    },
                                },
                                "required": ["enum"],
                            },
                            "kind": {
                                "type": "object",
                                "properties": {
                                    "enum": {
                                        "type": "array",
                                        "items": {"type": "string", "minLength": 1},
                                        "minItems": 1,
                                        "maxItems": 1,
                                    },
                                },
                                "required": ["enum"],
                            },
                            "action": {
                                "type": "object",
                                "properties": {
                                    "enum": {
                                        "type": "array",
                                        "items": {"type": "string", "minLength": 1},
                                        "minItems": 1,
                                        "maxItems": 1,
                                    },
                                },
                                "required": ["enum"],
                            },
                        },
                        "required": ["module", "kind", "action"],
                    },
                },
                "required": ["properties"],
            },
            "minItems": 1,
        }
    },
    "additionalProperties": False,
    "required": ["oneOf"],
}


class ModuleAlreadyLoaded(Exception):
    pass


class SchemaErrorMutipleTypes(Exception):
    pass


class SchemaErrorDefinitionAlreadyUsed(Exception):
    pass


class ForisSchemaValidationError(Exception):
    pass


class ForisValidationError(Exception):
    pass


class ForisValidator(object):

    @staticmethod
    def _get_all_jsons_in_dir(dir_path):
        return [
            f for f in os.listdir(dir_path)
            if os.path.isfile(os.path.join(dir_path, f)) and f.endswith(".json")
        ]

    @staticmethod
    def _load_definitions(definitions, file_path):
        with open(file_path) as f:
            try:
                schema = json.load(f)
            except JSONDecodeError as e:
                raise ForisValidationError(
                    "Error loading file {}, reason: {!r}".format(file_path, e)
                ) from e
            Draft4Validator.check_schema(schema)
            for new_definition, data in schema["definitions"].items():
                if new_definition in definitions:
                    raise SchemaErrorDefinitionAlreadyUsed(new_definition)
                definitions[new_definition] = data

    @staticmethod
    def _prepare_base_validator(modules_list):
        schema = copy.deepcopy(BASE_SCHEMA)
        schema["properties"]["module"]["enum"] = [e for e in modules_list]
        return Draft4Validator(schema, format_checker=format_checker)

    @staticmethod
    def _prepare_validator(module_name, schema):
        schema["$schema"] = "http://turris.cz/foris-schema-modules-%s#" % module_name

        # custom schema_for_schemas to validate module name as well
        schema_for_schemas = copy.deepcopy(SCHEMA_FOR_SCHEMAS)
        schema_for_schemas["properties"]["oneOf"]["items"]["properties"]["properties"][
            "properties"]["module"]["properties"]["enum"]["items"]["enum"] = [module_name]

        # Validate input schema
        try:
            schema_validate(schema, schema_for_schemas)
        except ValidationError as e:
            raise ForisSchemaValidationError(
                "Validation of json schema {} failed. Reason: {!r}".format(schema["$schema"], e)
            ) from e

        # Now check for unique combination (module, kind, action)
        used = set()
        for e in schema["oneOf"]:
            item = (
                e["properties"]["module"]["enum"][0],
                e["properties"]["kind"]["enum"][0],
                e["properties"]["action"]["enum"][0],
            )
            if item in used:
                raise SchemaErrorMutipleTypes(item)
            used.add(item)

        return Draft4Validator(schema, format_checker=format_checker)

    @property
    def base_schema(self):
        return copy.deepcopy(self.base_validator.schema)

    @property
    def error_schema(self):
        return copy.deepcopy(self.error_validator.schema)

    def get_module_schema(self, module_name):
        return self.validators[module_name].schema

    def __init__(self, schema_paths, definitions_paths=[]):
        self.definitions = {}
        self.validators = {}

        # Load definition files into self.definitions
        for path in definitions_paths:
            for definition_file in ForisValidator._get_all_jsons_in_dir(path):
                ForisValidator._load_definitions(
                    self.definitions, os.path.join(path, definition_file))

        # load modules into modules
        for schema_path in schema_paths:
            for module_file in ForisValidator._get_all_jsons_in_dir(schema_path):
                module_name = module_file[:-5]
                if module_name in self.validators:
                    raise ModuleAlreadyLoaded(module_name)
                try:
                    with open(os.path.join(schema_path, module_file)) as f:
                        schema = json.load(f)
                except json.JSONDecodeError as e:
                    raise ForisSchemaValidationError(
                        "Validation of json schema {} failed. Reason: {!r}".format(f.name, e)
                    ) from e

                # fill-in global definitions (local definitions are not overriden)
                definitions = schema.get("definitions", {})
                for name, definition, in self.definitions.items():
                    if name not in definitions:
                        definitions[name] = definition
                schema["definitions"] = definitions

                Draft4Validator.check_schema(schema)

                self.validators[module_name] = ForisValidator._prepare_validator(
                    module_name, schema)

        self.base_validator = ForisValidator._prepare_base_validator(self.validators.keys())
        self.error_validator = Draft4Validator(ERROR_SCHEMA, format_checker=format_checker)

    def validate(self, msg):
        self.base_validator.validate(msg)
        try:
            self.validators[msg["module"]].validate(msg)  # finally with module validator
        except ValidationError as exc:
            # Test whether it is an error message
            if self.error_validator.is_valid(msg):
                return  # Pass errror message

            # Prepare more verbose output
            schema = copy.deepcopy(self.validators[msg["module"]].schema)
            relevant_lines = [
                e for e in schema["oneOf"]
                if e["properties"]["action"]["enum"][0] == msg["action"]
                and e["properties"]["kind"]["enum"][0] == msg["kind"]
            ]
            if relevant_lines and len(relevant_lines) == 1:
                mini_schema = {
                    "$schema": schema["$schema"],
                    "definitions": schema["definitions"],
                }
                for k, v in relevant_lines[0].items():
                    mini_schema[k] = v

                # This should rise more verbose exception
                Draft4Validator(mini_schema, format_checker=format_checker).validate(msg)

            raise exc  # Raise original exception

    def is_valid(self, msg):
        if not self.base_validator.is_valid(msg):
            return False
        if not self.validators[msg["module"]].is_valid(msg):
            if self.error_validator.is_valid(msg):
                return True  # it is an error message
            else:
                return False

        return True
