# Foris schema

Library which validates whether the json matches the protocol use between Foris web and a configuration backend.

## Requirements

* python3
* jsonschema

## Installation

```bash
python3 setup.py install
```

# Schema format

The format should be jsonschema format (Draf 4) and it should fill some mandatory fields e.g.:

```json
{
	"oneOf": [
		{
			"description": "Reply to call get action in simple module",
			"properties": {
				"module": {"enum": ["simple"]},
				"kind": {"enum": ["reply"]},
				"action": {"enum": ["get"]},
				"data": {
					"type": "object",
					"properties": {
						"result": {"type": "boolean"}
					},
					"additionalProperties": false,
					"required": ["result"]
				}
			},
			"additionalProperties": false,
			"required": ["data"]
		}
	]
}
```

The mandatory fields are `kind`, `module`, `action`, optional `data`, `errors`.
Note that `module` should be the same as the file name, `action` should be string and `kind` should be one `request`, `reply`, `notification`.

### Definitions

Note that every schema file can use global definitions to reuse some parts of the schema:

```json
	{
		"definitions": {
		"lower": {
			"type": "string",
			"pattern": "^[a-z]+$"
		},
		...
			"small_string": {"$ref": "#/definitions/lower"}
		...
	}
```

For details see https://spacetelescope.github.io/understanding-json-schema/structuring.html

## Usage

To validate in your program/module:
```python
from foris_schema import ForisValidator
validator = ForisValidator(["path/to/dir/with/schemas"])
validator.validate({"module": "simple", "kind": "request", "action": "get"})
```

## Command line utility

Command line utility to check either `.json` _file_ or _raw input_ against a _schema_.

```bash
foris-schema [-d DEFINITION, ...] [-i INPUT|-r RAW-INPUT] SCHEMA [SCHEMA ...]
```

Example usage:
```bash
foris-schema schema/folder -i my-file.json
foris-schema schema/folder -r '{"module": "simple", "kind": "reply", "action": "get", "data": {"result": false}}'
```

At least one ``schema`` is mandatory. Input only if json is not provided in ``PIPE`` like this:
```bash
cat path/to/my.json | foris-schema schema/folder

# or provide raw string to python module
cat path/to/my.json | python -m json-schema schema/folder
```

You may also need to import some common definitions:
```bash
foris-schema schema/folder -d definitions/folder -i my-file.json

# be aware that both DEFINITONS and SCHEMAS are list items, thus:
foris-schema path/to/schema/one /to/another -d one/definition another/definition -i file.json

# ... is valid command
```

### Test command-line interface

```bash
# activate venv
source .venv/bin/activate
pip install pytest
pytest tests/test_cli.py
```