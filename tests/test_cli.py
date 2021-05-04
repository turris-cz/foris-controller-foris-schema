import pytest
import subprocess
import json

from pathlib import Path

from subprocess import PIPE

TMP_DIR = Path(__file__).parent.absolute() / 'tmp'

# constants
PROGRAM = 'foris-schema'
SIMPLE_SCHEMA = './tests/schemas/modules/simple'
BASE_COMMAND = [PROGRAM, SIMPLE_SCHEMA]

VALIDATION_ERROR_MSG = b"Failed validating \'additionalProperties\' in schema:"
BAD_INPUT_MSG = b"Input is not a valid json:\nkey: value\nanotherkey: value2\n"

SIMPLE_JSON = {
    "module": "simple", "kind": "reply", "action": "get",
    "data": {"result": False}
}
SIMPLE_ERROR = {
    "module": "simple", "kind": "reply", "action": "get",
    "data": {"result": False},
    "extra": "YES"
}


@pytest.fixture()
def mock_file(request, tmp_path):
    f_path = tmp_path / 'test.json'
    with open(f_path, 'w') as f:
        json.dump(request.param, f)
    yield str(f_path)


def test_command_works():
    res = subprocess.run([PROGRAM, '--help'], stdin=None, stdout=subprocess.DEVNULL)
    assert res.returncode == 0


def test_command_requires_arguments():
    res = subprocess.run([PROGRAM], stderr=PIPE, stdin=None)
    assert res.returncode == 2
    assert b'following arguments are required: schemas' in res.stderr


def test_file_not_exists():
    command = [*BASE_COMMAND, '-i', 'tmp/some_file_does_not_exist.json']
    ret = subprocess.run(command, stderr=PIPE, stdin=None)
    assert ret.returncode == 1
    assert b'FileNotFoundError:' in ret.stderr


def test_pipe_not_json():
    data = b'key: value\nanotherkey: value2'
    ret = subprocess.run(BASE_COMMAND, input=data, stderr=PIPE)
    assert ret.returncode == 1
    assert BAD_INPUT_MSG in ret.stderr


@pytest.mark.parametrize('mock_file,retval,msg', [
    (SIMPLE_JSON, 0, b''),
    (SIMPLE_ERROR, 1, VALIDATION_ERROR_MSG),
], indirect=['mock_file'])
def test_command_input(mock_file, retval, msg):
    command = [*BASE_COMMAND, '-i', mock_file]
    ret = subprocess.run(command, stdin=None, stderr=PIPE)
    assert ret.returncode == retval
    assert msg in ret.stderr


@pytest.mark.parametrize('mock_json,retval,msg', [
    (SIMPLE_JSON, 0, b''),
    (SIMPLE_ERROR, 1, VALIDATION_ERROR_MSG)
])
def test_pipe_input(mock_json, retval, msg):
    data = bytes(json.dumps(mock_json), 'utf-8')
    ret = subprocess.run(BASE_COMMAND, input=data, stderr=PIPE)
    assert ret.returncode == retval
    assert msg in ret.stderr
