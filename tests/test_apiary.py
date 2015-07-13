__author__ = 'admin'

from unittest import TestCase
from pre_commit_hook.apiary import ApiaryValidator
from pre_commit_hook.apiary import _state_read_group_title
from pre_commit_hook.apiary import _state_read_api_title
from pre_commit_hook.apiary import _state_read_api_method
from pre_commit_hook.apiary import _state_read_param_tag
from pre_commit_hook.apiary import _state_read_request_tag
from pre_commit_hook.apiary import _state_read_response_tag
from pre_commit_hook.error import ApiaryError, ApiarySyntaxError


_TEST_API_TITLE             = '## test api [/test/api/pattern]'
_TEST_API_METHOD_TEMPLATE   = '### api action [%s]'
_TEST_PARAMETER_TAG         = '+ Parameters'
_TEST_PARAMETER_STRING      = '     + test  (number) ... descriptions'
_TEST_REQUEST_TAG           = '+ Request IssueOrders (application/json)'
_TEST_RESPONSE_TAG          = '+ Response 200 (application/json)'

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

    # ------------------------------------------------------------------------------------------------------------------
    # Test Case: read_response_tag
    # ------------------------------------------------------------------------------------------------------------------
    def test_read_line_state_read_response_tag(self):
        v = ApiaryValidator()
        state = _state_read_response_tag

    # ------------------------------------------------------------------------------------------------------------------
    # Utilities:
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

    def _test_with_request_content(self, validator, content_file, expected_error_line_counts=list()):
        print('\nTest with request from: %s' % content_file)
        validator.state = _state_read_request_tag
        with open(content_file, 'r') as f:
            lines = f.readlines()

        self._test_with_lines_of_content(validator, lines, expected_error_line_counts)

    def _test_with_response_content(self, validator, content_file, expected_error_line_counts=list()):
        validator.state = _state_read_response_tag
        print('\nTest with response from: %s' % content_file)
        with open(content_file, 'r') as f:
            lines = f.readlines()

        self._test_with_lines_of_content(validator, lines, expected_error_line_counts)

    def _test_with_lines_of_content(self, validator, lines, expected_error_line_counts):
        line_count = 0
        for line in lines:
            line_count += 1
            valid, error = validator._read_line(line)
            if line_count in expected_error_line_counts:
                self.assertFalse(valid)
                self.assertEqual(error.type, ApiarySyntaxError().type)
            else:
                if error:
                    print('error(@ line %d): %s' % (line_count,error))
                self.assertTrue(valid)
                self.assertEqual(error, None)
