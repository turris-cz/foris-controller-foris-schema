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
        },
    },
    "allOf": [
        {"$ref": "#/definitions/message"},
        {"oneOf": []},
    ]
}


class ModuleAlreadyLoaded(Exception):
    pass


class ModuleNotFound(Exception):
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

    def validate(self, msg, module=None, idx=None):
        schema = copy.deepcopy(BASE_SCHEMA)

        # load definitions
        for _, stored_module in self.modules.items():
            if "definitions" in stored_module:
                schema["definitions"].update(stored_module["definitions"])

        if idx is not None:
            del schema["allOf"][1]
            schema["allOf"].append(self.modules[module]["oneOf"][idx])
            schema_validate(msg, schema)
            return

        modules = list(self.modules.keys()) if module is None else [module]
        for module in modules:
            if module not in self.modules:
                raise ModuleNotFound(module)
            definitions = self.modules[module]
            schema["allOf"][1]["oneOf"].extend(definitions["oneOf"])
        schema_validate(msg, schema)
