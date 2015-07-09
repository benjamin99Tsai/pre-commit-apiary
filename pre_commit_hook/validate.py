__author__ = 'admin'

import argparse
import os

# ----------------------------------------------------------------------------------------------------------------------
# validate the single file with the filename:
def _validate_with_filename(filename):
    print('start validate file: %s/%s' % (os.getcwd(), filename))
    return 0

# ----------------------------------------------------------------------------------------------------------------------
# Define the entry point for executing the validation
def validate(argv=None):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('filenames', nargs='*', help='Filenames to validate')
    args = arg_parser.parse_args(argv)

    for filename in args.filenames:
        _validate_with_filename(filename)

    return 0
