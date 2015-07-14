__author__ = 'admin'

import re
import json
from unittest import TestCase
from os import listdir
from os import path
from pre_commit_hook.apiary import ApiaryValidator
from pre_commit_hook.apiary import _state_read_group_title
from pre_commit_hook.apiary import _state_read_api_title
from pre_commit_hook.apiary import _state_read_api_method
from pre_commit_hook.apiary import _state_read_param_tag
from pre_commit_hook.apiary import _state_read_request_tag
from pre_commit_hook.apiary import _state_read_response_tag
from pre_commit_hook.error import ApiaryError, ApiarySyntaxError, ApiaryParameterNotDefinedError

_TEST_API_TITLE = '## test api [/test/api/pattern]'
_TEST_API_METHOD_TEMPLATE = '### api action [%s]'
_TEST_PARAMETER_TAG = '+ Parameters'
_TEST_PARAMETER_STRING = '     + test  (number) ... descriptions'
_TEST_REQUEST_TAG = '+ Request IssueOrders (application/json)'
_TEST_RESPONSE_TAG = '+ Response 200 (application/json)'
_TEST_TYPE_REQUEST_CONTENT = 0
_TEST_TYPE_RESPONSE_CONTENT = 1

_current_file_path = path.dirname(path.abspath(__file__))


class ApiaryTest(TestCase):
    # ------------------------------------------------------------------------------------------------------------------
    # Test Case: read_group_title
    # ------------------------------------------------------------------------------------------------------------------
    def test_read_line_state_read_group_title(self):
        v = ApiaryValidator()
        state = _state_read_group_title
        self._test_read_line(line=' ',
                             validator=v,
                             state=state,
                             expected_state=_state_read_group_title)

        self._test_read_line(line=_TEST_API_TITLE,
                             validator=v,
                             state=state,
                             expected_state=_state_read_api_title)

        for method in ['GET', 'POST', 'PUT', 'DELETE']:
            self._test_read_line(line=_TEST_API_METHOD_TEMPLATE % method,
                                 validator=v,
                                 state=state,
                                 expected_error=ApiarySyntaxError())

        self._test_read_line(line=_TEST_PARAMETER_TAG,
                             validator=v,
                             state=state,
                             expected_error=ApiarySyntaxError())

        self._test_read_line(line=_TEST_PARAMETER_STRING,
                             validator=v,
                             state=state,
                             expected_error=ApiarySyntaxError())

        self._test_read_line(line=_TEST_REQUEST_TAG,
                             validator=v,
                             state=state,
                             expected_error=ApiarySyntaxError())

        self._test_read_line(line=_TEST_RESPONSE_TAG,
                             validator=v,
                             state=state,
                             expected_error=ApiarySyntaxError())

    # ------------------------------------------------------------------------------------------------------------------
    # Test Case: read_api_title
    # ------------------------------------------------------------------------------------------------------------------
    def test_read_line_state_read_api_title(self):
        v = ApiaryValidator()
        state = _state_read_api_title
        self._test_read_line(line=' ',
                             validator=v,
                             state=state,
                             expected_state=_state_read_api_title)

        for method in ['GET', 'POST', 'DELETE', 'PUT']:
            self._test_read_line(line=_TEST_API_METHOD_TEMPLATE % method,
                                 state=state,
                                 validator=v,
                                 expected_state=_state_read_api_method)

        self._test_read_line(line=_TEST_PARAMETER_TAG,
                             state=state,
                             validator=v,
                             expected_error=ApiarySyntaxError())

        self._test_read_line(line=_TEST_PARAMETER_STRING,
                             state=state,
                             validator=v,
                             expected_error=ApiarySyntaxError())

        self._test_read_line(line=_TEST_REQUEST_TAG,
                             state=state,
                             validator=v,
                             expected_error=ApiarySyntaxError())

        self._test_read_line(line=_TEST_RESPONSE_TAG,
                             state=state,
                             validator=v,
                             expected_error=ApiarySyntaxError())

    # ------------------------------------------------------------------------------------------------------------------
    # Test Case: read_api_method
    # ------------------------------------------------------------------------------------------------------------------
    def test_read_line_state_read_api_method(self):
        v = ApiaryValidator()
        state = _state_read_api_method
        self._test_read_line(line=' ',
                             state=state,
                             validator=v,
                             expected_state=state)

        self._test_read_line(line=_TEST_PARAMETER_TAG,
                             state=state,
                             validator=v,
                             expected_state=_state_read_param_tag)

        self._test_read_line(line=_TEST_PARAMETER_STRING,
                             state=state,
                             validator=v,
                             expected_error=ApiarySyntaxError())

        self._test_read_line(line=_TEST_REQUEST_TAG,
                             state=state,
                             validator=v,
                             expected_state=_state_read_request_tag)

        self._test_read_line(line=_TEST_RESPONSE_TAG,
                             state=state,
                             validator=v,
                             expected_state=_state_read_response_tag)

    # ------------------------------------------------------------------------------------------------------------------
    # Test Case: read_param_tag
    # ------------------------------------------------------------------------------------------------------------------
    def test_read_line_state_read_param_tag(self):
        v = ApiaryValidator()
        v._parameters = ['test']
        state = _state_read_param_tag
        self._test_read_line(line=' ',
                             state=state,
                             validator=v,
                             expected_state=state)

        self._test_read_line(line=_TEST_PARAMETER_TAG,
                             state=state,
                             validator=v,
                             expected_error=ApiarySyntaxError())

        self._test_read_line(line=_TEST_PARAMETER_STRING,
                             state=state,
                             validator=v,
                             expected_state=state)

        self._test_read_line(line=_TEST_REQUEST_TAG,
                             state=state,
                             validator=v,
                             expected_state=_state_read_request_tag)

        self._test_read_line(line=_TEST_RESPONSE_TAG,
                             state=state,
                             validator=v,
                             expected_state=_state_read_response_tag)

    # ------------------------------------------------------------------------------------------------------------------
    # Test Case: read_request_tag
    # ------------------------------------------------------------------------------------------------------------------
    def test_read_line_state_read_request_tag(self):
        v = ApiaryValidator()
        state = _state_read_request_tag
        self._test_read_line(line=' ',
                             state=state,
                             validator=v,
                             expected_state=_state_read_request_tag)

    def test_read_line_state_read_request_with_valid_request_content(self):
        v = ApiaryValidator()
        request_path = '%s/request/' % _current_file_path
        files = [f for f in listdir(request_path) if path.isfile(path.join(request_path, f))]
        for f in files:
            if re.match(r'request_good_(.+).json', f):
                content_file = path.join(request_path, f)
                self._test_with_request_content(validator=v, content_file=content_file)

    def test_read_line_state_read_request_with_invalid_request_content(self):
        v = ApiaryValidator()
        request_path = '%s/request/' % _current_file_path
        self._test_invalid_template(validator=v,
                                    template=path.join(request_path, 'request_template.json'),
                                    test_type=_TEST_TYPE_REQUEST_CONTENT)

    # ------------------------------------------------------------------------------------------------------------------
    # Test Case: read_response_tag
    # ------------------------------------------------------------------------------------------------------------------
    def test_read_line_state_read_response_tag(self):
        v = ApiaryValidator()
        state = _state_read_response_tag
        self._test_read_line(line=' ',
                             state=state,
                             validator=v,
                             expected_state=_state_read_response_tag)

    def test_read_line_state_read_response_tag_with_valid_response_content(self):
        v = ApiaryValidator()
        responses_path = '%s/response/' % _current_file_path
        files = [f for f in listdir(responses_path) if path.isfile(path.join(responses_path, f))]
        for f in files:
            if re.match(r'response_good_(.+)\.json', f):
                content_file = path.join(responses_path, f)
                self._test_with_response_content(validator=v, content_file=content_file)

    def test_read_line_state_read_response_tag_with_invalid_response_content(self):
        v = ApiaryValidator()
        response_path = '%s/response/' % _current_file_path
        self._test_invalid_template(validator=v,
                                    template=path.join(response_path, 'response_template.json'),
                                    test_type=_TEST_TYPE_RESPONSE_CONTENT)

    # ------------------------------------------------------------------------------------------------------------------
    # Test Case: validate the parameter related issues
    # ------------------------------------------------------------------------------------------------------------------
    def test_get_parameters(self):
        test_title = '## TEST API [/test/api/pattern/{param_1}/with/{param_2}/{?p1,p2,p3}]'
        expected = ['param_1', 'param_2', 'p1', 'p2', 'p3']
        results  = ApiaryValidator._get_parameters_from_api_title(test_title)
        self.assertEqual(results, expected)

    def test_get_parameter_from_parameter_string(self):
        expected = 'parameter_Name-000123'
        test_string = ' + %s     (number) ... Some descriptions' % expected
        result = ApiaryValidator._get_parameter_from_parameter_string(test_string)
        self.assertEqual(result, expected)

    def test_read_api_title_with_parameters(self):
        v = ApiaryValidator()
        test_title = '## TEST API [/test/api/pattern/{param_1}/with/{param_2}/{?p1,p2,p3}]'
        v.state = _state_read_group_title
        v._read_line(test_title)
        expected = ['param_1', 'param_2', 'p1', 'p2', 'p3']
        results = v._parameters
        self.assertEqual(results, expected)

    def test_check_if_parameter_is_defined(self):
        v = ApiaryValidator()
        v.state = _state_read_param_tag
        v._parameters = ['p1', 'p2', 'p3']

        valid, error = v._read_line('+ p1   (string) ... test parameter 1')
        self.assertTrue(valid)

        valid, error = v._read_line('       + p2 (string) ... test parameter 2')
        self.assertTrue(valid)

        valid, error = v._read_line('+ p4 (string) ... test parameter 3')
        self.assertFalse(valid)
        self.assertEqual(error.type, ApiaryParameterNotDefinedError(parameter='p4').type)

    # ------------------------------------------------------------------------------------------------------------------
    # Utilities for testing:
    # ------------------------------------------------------------------------------------------------------------------
    def _test_read_line(self, line, validator, state, expected_state=None, expected_error=None):
        validator.state = state
        valid, error = validator._read_line(line)
        if expected_error is None:
            self.assertTrue(valid)
            if expected_state is not None:
                self.assertEqual(validator.state, expected_state)
        else:
            assert isinstance(expected_error, ApiaryError)
            self.assertFalse(valid)
            self.assertTrue(isinstance(error, ApiaryError))
            self.assertEqual(error.type, expected_error.type)

    def _test_with_request_content(self, validator, content_file, expected_error_line_count=None):
        print('\nTest with request from: %s' % content_file)
        validator.state = _state_read_request_tag
        with open(content_file, 'r') as f:
            lines = f.readlines()

        self._test_with_lines_of_content(validator, lines, expected_error_line_count)

    def _test_with_response_content(self, validator, content_file, expected_error_line_count=None):
        validator.state = _state_read_response_tag
        print('\nTest with response from: %s' % content_file)
        with open(content_file, 'r') as f:
            lines = f.readlines()

        self._test_with_lines_of_content(validator, lines, expected_error_line_count)

    def _test_with_lines_of_content(self, validator, lines, expected_error_line_count):
        line_count = 0
        for line in lines:
            line_count += 1
            valid, error = validator._read_line(line)
            if line_count == expected_error_line_count:
                self.assertFalse(valid)
                self.assertEqual(error.type, ApiarySyntaxError().type)
                break
            else:
                if error:
                    print('error(@ line %d): %s' % (line_count, error))
                self.assertTrue(valid)
                self.assertEqual(error, None)

    # ------------------------------------------------------------------------------------------------------------------
    # Utilities for parsing the template for invalid request/response content:
    # ------------------------------------------------------------------------------------------------------------------
    def _test_invalid_template(self, validator, template, test_type):
        assert test_type in [_TEST_TYPE_REQUEST_CONTENT, _TEST_TYPE_RESPONSE_CONTENT]
        assert isinstance(template, str), 'the template should be a string indicates the file path'
        with open(template, 'r') as f:
            lines = f.readlines()

        current_file_path = path.dirname(path.abspath(__file__))
        if test_type == _TEST_TYPE_REQUEST_CONTENT:
            test_function = self._test_with_request_content
            test_path = '%s/request/' % current_file_path
        else:
            test_function = self._test_with_response_content
            test_path = '%s/response/' % current_file_path

        test_cases = json.loads(''.join(lines))
        for case in test_cases.get('content'):
            test_function(validator=validator,
                          content_file=path.join(test_path, case.get('filename')),
                          expected_error_line_count=case.get('error_line_count'))