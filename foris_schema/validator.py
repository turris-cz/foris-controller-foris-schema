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

import copy
import json
import os

from jsonschema import validate as schema_validate, Draft4Validator


BASE_SCHEMA = {
    "$schema": "http://turris.cz/foris-schema#",
    "definitions": {
        "message": {
            "type": "object",
            "properties": {
                "kind": {"enum": ["request", "reply", "notification"]},
                "module": {"type": "string"},
                "action": {"type": "string"},
                "data": {"type": "object"},
            },
            "required": ["kind", "module", "action"],
            "additionalProperties": False,
        },
    },
    "allOf": [
        {"$ref": "#/definitions/message"},
        {"oneOf": []},
    ]
}


class ModuleAlreadyLoaded(Exception):
    pass


class SchemaErrorMutipleTypes(Exception):
    pass


class SchemaErrorWrongMessage(Exception):
    pass


class SchemaErrorModuleMismatch(Exception):
    pass


class SchemaErrorDefinitionAlreadyUsed(Exception):
    pass


class ForisValidator(object):
    def __init__(self, schema_paths):
        self.modules = {}
        # Get json files
        for path in schema_paths:
            names = [
                f[:-5] for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f)) and f.endswith(".json")
            ]

            for module_name in names:
                if module_name in self.modules:
                    raise ModuleAlreadyLoaded(module_name)
                with open(os.path.join(path, module_name + ".json")) as f:
                    schema = json.load(f)
                    Draft4Validator.check_schema(schema)
                    self.modules[module_name] = schema

        # Merge modules and create an object
        schema = copy.deepcopy(BASE_SCHEMA)
        self._extend_modules(schema)
        self._load_definitions(schema)
        self._validator = Draft4Validator(schema)

    def _load_definitions(self, schema):
        for _, stored_module in self.modules.items():
            if "definitions" in stored_module:
                for new_definition in stored_module["definitions"].keys():
                    if new_definition in schema["definitions"]:
                        raise SchemaErrorDefinitionAlreadyUsed(new_definition)
                schema["definitions"].update(stored_module["definitions"])

    def _filter_module(self, module, kind=None, action=None):
        module = copy.deepcopy(module)
        if kind or action:
            filtered = filter(
                lambda x:
                    "properties" in x and
                    "module" in x["properties"] and "enum" in x["properties"]["module"] and
                    "kind" in x["properties"] and "enum" in x["properties"]["kind"] and
                    "action" in x["properties"] and "enum" in x["properties"]["action"],
                module["oneOf"]
            )
            if kind:
                filtered = filter(
                    lambda x: kind in x["properties"]["kind"]["enum"], filtered
                )
            if action:
                filtered = filter(
                    lambda x: action in x["properties"]["action"]["enum"], filtered
                )
            module["oneOf"] = filtered

        return module

    def _check_message_type(self, obj):
        if "properties" not in obj:
            raise SchemaErrorWrongMessage("missing properties attribute in: %s" % obj)
        if not {"kind", "module", "action"}.issubset(obj["properties"].keys()):
            raise SchemaErrorWrongMessage("kind, module, action are required: %s" % obj)
        for name in ("kind", "module", "action"):
            if "enum" not in obj["properties"][name]:
                continue
            if len(obj["properties"][name]["enum"]) != 1:
                raise SchemaErrorWrongMessage(
                    "only single enum choice allowed for %s in: %s" % (name, obj))

    def _extend_modules(self, schema, module_name=None, kind=None, action=None):
        modules = list(self.modules.keys()) if module_name is None else [module_name]
        types = set()
        for module_name in modules:
            if module_name in self.modules:
                module = self._filter_module(self.modules[module_name], kind, action)
            else:
                continue

            # Pefrorm some checks
            for obj in module["oneOf"]:
                self._check_message_type(obj)
                if "enum" not in obj["properties"]["module"]:
                    continue
                module_name_sch = obj["properties"]["module"]["enum"][0]
                if module_name != module_name_sch:
                    raise SchemaErrorModuleMismatch(
                        "'%s' != '%s'" % (module_name, module_name_sch))
                if "enum" not in obj["properties"]["kind"] \
                        or "enum" not in obj["properties"]["action"]:
                    continue
                kind = obj["properties"]["kind"]["enum"][0]
                action = obj["properties"]["action"]["enum"][0]
                if (module_name, kind, action) in types:
                    raise SchemaErrorMutipleTypes((module_name, kind, action))
                else:
                    types.add((module_name, kind, action))

            schema["allOf"][1]["oneOf"].extend(module["oneOf"])

    def _match_base(self, msg):
        schema = copy.deepcopy(BASE_SCHEMA)
        del schema["allOf"][1]
        schema_validate(msg, schema)

    def _match_filtered(self, msg):
        # suppose that it already matched base
        schema = copy.deepcopy(BASE_SCHEMA)
        self._extend_modules(schema, msg["module"], msg["kind"], msg["action"])

        if len(schema["allOf"][1]["oneOf"]) == 1:
            element = schema["allOf"][1]["oneOf"][0]
            del schema["allOf"][1]
            schema["allOf"].append(element)
        else:
            # multiple options or no option left - perform ordinary validation
            self.validate(msg)
            return

        schema_validate(msg, schema)

    @property
    def schema(self):
        return copy.deepcopy(self._validator.schema)

    def validate(self, msg):
        self._validator.validate(msg)

    def validate_verbose(self, msg):
        self._match_base(msg)
        self._match_filtered(msg)
