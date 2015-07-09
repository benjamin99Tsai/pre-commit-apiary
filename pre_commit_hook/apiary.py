__author__ = 'Arsenal_49'

import re

# Define the pattern match/search
_group_title    = re.compile(r'^#(\s)+.*').match
_api_title      = re.compile(r'^##.*\[\/.+\]$').match
_api_url        = re.compile(r'\[\/[a-zA-Z0-9\ \_\-\/\{/}]*[\{\]]').search
_api_method     = re.compile(r'\[(GET|POST|PUT|DELETE|PATCH)\]').search
_param_title    = re.compile(r'^\+ Parameters').match
_param_string   = re.compile(r'^\s*\+\s*[a-zA-Z0-9\_\-]+\s*\([a-zA-Z\_\-0-9]+\)\s*[(\.){3}]?.*').match
_request_title  = re.compile(r'^\+ Request .+').search
_response_title = re.compile(r'^\+ Response').match

# Define the static states for validation process:
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
