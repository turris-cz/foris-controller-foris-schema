import argparse
import json
from json.decoder import JSONDecodeError
from sys import stdin
from foris_schema.validator import ForisValidator


class NotJson(Exception):
    pass


def _inject_input_args(p: argparse.ArgumentParser):
    """p: parser"""
    inputs = p.add_mutually_exclusive_group(required=True)
    inputs.add_argument(
        '-i',
        metavar='FILE',
        type=str,
        help='Name or path of file to by validated.'
    )
    inputs.add_argument(
        '-r',
        metavar="'{RAW INPUT}'",
        type=str,
        help='Raw-string json input.')


def main():
    """ We do not need to handle non-existent schema paths as ForisValidator already
catches such errors. """

    parser = argparse.ArgumentParser(
        prog='foris-schema',
        description='''Validates input json file against schema.
You can also provide JSON using stdin PIPE.'''
    )
    parser.add_argument(
        '-d',
        metavar='PATH',
        nargs="*",
        help='Paths to folders containing custom defintions. Not required.'
    )

    # input file
    input_json = None

    if stdin.isatty():
        # if input JSON string is provided by pipe below arguments are not required.
        _inject_input_args(parser)
    else:
        # check wheter we can parse stream to json
        in_stream = stdin.read()
        try:
            input_json = json.loads(in_stream)
        except JSONDecodeError as e:
            if in_stream == '':
                # in Docker environment empty b'' is passed to PIPE no matter what
                _inject_input_args(parser)
            else:
                raise NotJson(f"Input is not a valid json:\n{in_stream}") from e

    parser.add_argument(
        'schemas',
        nargs="+",
        help='Paths to folders with schemas to validate against.'
    )

    args = parser.parse_args()

    # prepare validator
    validator = ForisValidator(args.schemas, args.d or [])

    # prepare data provided using either `-i` or `-r` arguments
    if input_json is None:
        if args.r is not None:
            input_json = json.loads(args.r)

        if args.i is not None:
            with open(args.i, 'r') as f:
                input_json = json.load(f)

    validator.validate(input_json)


if __name__ == '__main__':
    main()
