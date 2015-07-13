__author__ = 'Arsenal_49'

import re
from pre_commit_hook.decoder import ApiDecoder as ContentDecoder
from pre_commit_hook.error import ApiarySyntaxError

# Define the pattern match/search
_group_title    = re.compile(r'^#(\s)+.*').match
_api_title      = re.compile(r'^##(\s)+.*\[\/.+\]$').match
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
_state_error                = -1

# ----------------------------------------------------------------------------------------------------------------------
# define the Validator class
class ApiaryValidator:
    def __init__(self):
        self.state = _state_init
        self.decoder = ContentDecoder()
        self._read_parameter_string = False

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
        assert self.state > 0, 'StateError: the validator is in the error state'

        if self.state == _state_read_group_title:
            if _api_title(line):
                if not _api_url(line):
                    error = ApiarySyntaxError(message='Cannot find the api url in line: %s' % line)
                    self.state = _state_error
                else:
                    self.state = _state_read_api_title

            elif _api_method(line) or _param_title(line) or _param_string(line) or _request_title(line) \
                    or _response_title(line):
                error = ApiarySyntaxError(message='Missing api title string')
                self.state = _state_error

        elif self.state == _state_read_api_title:
            if _api_method(line):
                self.state = _state_read_api_method

            elif _param_title(line) or _param_string(line) or _request_title(line) or _response_title(line):
                error = ApiarySyntaxError(message='Missing api method string')
                self.state = _state_error

        elif self.state == _state_read_api_method:
            if _param_title(line):
                self._read_parameter_string = False
                self.state = _state_read_param_tag

            elif _request_title(line):
                self.decoder.clear()
                self.state = _state_read_request_tag

            elif _response_title(line):
                self.decoder.clear()
                self.state = _state_read_response_tag

            elif _param_string(line):
                error = ApiarySyntaxError(message='Missing parameter title')
                self.state = _state_error

        elif self.state == _state_read_param_tag:
            if _param_string(line):
                self._read_parameter_string = True

            elif _request_title(line):
                if not self._read_parameter_string:
                    error = ApiarySyntaxError(message='Missing parameter info')
                    self.state = _state_error
                else:
                    self.decoder.clear()
                    self.state = _state_read_request_tag

            elif _response_title(line):
                if not self._read_parameter_string:
                    error = ApiarySyntaxError(message='Missing parameter info')
                    self.state = _state_error
                else:
                    self.decoder.clear()
                    self.state = _state_read_response_tag

            elif not re.match(r'\s+', line):
                error = ApiarySyntaxError(message='The lines should contain the parameter info')
                self.state = _state_error

        elif self.state == _state_read_request_tag:
            if _response_title(line):
                if not self.decoder.get_parsed_objects():
                    error = ApiarySyntaxError(message='Missing request content')
                    self.state = _state_error
                else:
                    self.decoder.clear()
                    self.state = _state_read_response_tag
            else:
                try:
                    self.decoder.scan_line(line)
                except Exception as e:
                    error = ApiarySyntaxError(message='DecodeException: %s' % e.message)
                    self.state = _state_error

        elif self.state == _state_read_response_tag:
            if _group_title(line):
                if not self.decoder.get_parsed_objects():
                    error = ApiarySyntaxError(message='Missing response content')
                    self.state = _state_error
                else:
                    self.decoder.clear()
                    self.state = _state_read_group_title

            elif _api_title(line):
                if not self.decoder.get_parsed_objects():
                    error = ApiarySyntaxError(message='Missing response content')
                    self.state = _state_error
                else:
                    self.decoder.clear()
                    self.state = _state_read_api_title

            else:
                try:
                    self.decoder.scan_line(line)

                except AssertionError as e:
                    error = ApiarySyntaxError(message='DecodeAssertion: %s' % e.args)
                    self.state = _state_error

                except Exception as e:
                    error = ApiarySyntaxError(message='DecodeException: %s' % e.message)
                    self.state = _state_error

        else:   # _state_init
            if _group_title(line):
                self._state = _state_read_group_title

        return (error is None), error
