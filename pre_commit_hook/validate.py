__author__ = 'admin'

import argparse
import os

# define the static states for validation process:
_state_init                 = 0
_state_read_group_title     = 1
_state_read_api_title       = 2
_state_read_api_method      = 3
_state_read_param_tag       = 4
_state_read_request_tag     = 5
_state_read_response_tag    = 6

# ----------------------------------------------------------------------------------------------------------------------
# define the Validator class
class ApiaryValidator:
    # define the states:

    def __init__(self):
        self.state = _state_init

    def validate_file(self, file):
        validation_result = True
        assert isinstance(file, str)
        try:
            with open(file, 'r') as f:
                lines = f.readlines()

        except FileNotFoundError:
            print('Error: could not find the file %s' % file)
            lines = list()
            validation_result = False

        line_count = 0
        for line in lines:
            line_count += 1
            valid, error = self._read_line(line)
            if not valid:
                print('ValError: %s (@ %d)' % (error.message, line_count))
                validation_result = False
                break
        return validation_result

    def _read_line(self, line):
        error = None

        if self.state == _state_read_group_title:
            pass

        elif self.state == _state_read_api_title:
            pass

        elif self.state == _state_read_api_method:
            pass

        elif self.state == _state_read_param_tag:
            pass

        elif self.state == _state_read_request_tag:
            pass

        elif self.state == _state_read_response_tag:
            pass

        else:   # _state_init
            pass

        return (error is None), error



# ----------------------------------------------------------------------------------------------------------------------
# validate the single file with the filename:
def _validate_with_filename(filename):
    file_path = '%s/%s' % (os.getcwd(), filename)
    print('start validate file: %s' % file_path)
    validator = ApiaryValidator()
    validator.validate_file(file_path)

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

    return result
