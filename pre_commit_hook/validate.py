__author__ = 'Arsenal_49'

from pre_commit_hook.apiary import ApiaryValidator
import argparse
import os

# ----------------------------------------------------------------------------------------------------------------------
# validate the single file with the filename:
def _validate_with_filename(filename):
    file_path = '%s/%s' % (os.getcwd(), filename)
    print('start validate file: %s' % file_path)
    validator = ApiaryValidator()
    return validator.validate_file(file_path)

# ----------------------------------------------------------------------------------------------------------------------
# Define the entry point for executing the validation
def validate(argv=None):
    result = 0
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('filenames', nargs='*', help='Filenames to validate')
    args = arg_parser.parse_args(argv)

    for filename in args.filenames:
        if not _validate_with_filename(filename):
            print('validation not pass with file: %s' % filename)
            result = -1
            break
        else:
            print('validation pass with file: %s' % filename)

    return result
