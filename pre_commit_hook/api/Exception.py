__author__ = 'admin'


# ----------------------------------------------------------------------------------------------------------------------
# The Base Exception for Testing
# ----------------------------------------------------------------------------------------------------------------------
class TestingException(Exception):
    def __init__(self, **kwargs):
        self.message = kwargs.get('message', None)
        self.code = kwargs.get('code', 400)
        self.user_info = kwargs.get('user_info', dict())

    def __str__(self):
        return "error %d: %s" % (self.code, self.message)


# ----------------------------------------------------------------------------------------------------------------------
# The API Syntax Related Exception(s):
# ----------------------------------------------------------------------------------------------------------------------
class ApiParsingException(TestingException):
    def __init__(self, message, line_count=-1):
        assert isinstance(line_count, int) and isinstance(message, str)
        self.prefix = '[Syntax Error]'
        user_info = dict()
        user_info['line_count'] = line_count
        super(ApiParsingException, self).__init__(
            message='%s %s' % (self.prefix, message),
            code=801,
            user_info=user_info
        )

    def set_line_count(self, line_count):
        assert line_count > 0, 'the input line count should > 0'
        self.user_info['line_count'] = line_count
        self.message = '%s (@ line: %d) %s' % (self.prefix, line_count, self._get_message_without_prefix())

    def _get_message_without_prefix(self):
        import re

        message = self.message
        prefix = self.prefix.replace('[', '\[').replace(']', '\]')
        prefix_search = re.search(prefix, message)
        if prefix_search:
            message = message[prefix_search.end() + 1:]
        return message


# ----------------------------------------------------------------------------------------------------------------------
# The Testing Target Related Exception(s):
# ----------------------------------------------------------------------------------------------------------------------
class UrlNotReachException(TestingException):
    def __init__(self, url, reason='', status_code=404, content=None):
        assert isinstance(url, str) and isinstance(status_code, int) and isinstance(reason, str)
        super(UrlNotReachException, self).__init__(
            message="Could not reach the target with the url: %s \nReason: %s" % (url, reason),
            code=status_code,
            user_info={'content': content}
        )


class ApiKeyPathNotFoundException(TestingException):
    def __init__(self, key_path, url):
        assert isinstance(key_path, str) and isinstance(url, str)
        super(ApiKeyPathNotFoundException, self).__init__(
            message='The key path: %s is not valid for response from: %s' % (key_path, url),
            code=500,
            user_info={}
        )

# ----------------------------------------------------------------------------------------------------------------------
# The Parameter Related Exception(s):
# ----------------------------------------------------------------------------------------------------------------------
class ParameterNotValidException(TestingException):
    def __init__(self, key, expected_type):
        assert isinstance(key, str)
        assert isinstance(expected_type, str)
        user_info = {
            "key": key,
            "expected_type": expected_type,
        }
        super(ParameterNotValidException, self).__init__(
            message='The parameter with key (%s) is not valid with type (%s)'
                    % (key, expected_type),
            code=500,
            user_info=user_info)


class ResponseParameterTypeNotMatchException(TestingException):
    def __init__(self, expected_type, resolved_type):
        super(ResponseParameterTypeNotMatchException, self).__init__(
            message="The parameter type (%s) did not match the expected one (%s)" \
                    % (expected_type, resolved_type),
            code=500,
            user_info={}
        )


class MissingParameterException(TestingException):
    def __init__(self, key):
        assert isinstance(key, str)
        super(MissingParameterException, self).__init__(
            message='Missing parameter with key %s' % key,
            code=500,
            user_info={"key": key})


# ----------------------------------------------------------------------------------------------------------------------
# The Response Related Exception(s):
# ----------------------------------------------------------------------------------------------------------------------
class ResponseNotFoundException(TestingException):
    # should raise this exception when the returned status code is not found in the template file
    def __init__(self, status_code):
        assert isinstance(status_code, int)
        super(ResponseNotFoundException, self).__init__(
            message='Could not found response with status code: %d' % status_code,
            code=900,
            user_info={})

class ResponseContentJsonException(TestingException):
    def __init__(self, message, content):
        assert isinstance(message, str)
        super(ResponseContentJsonException, self).__init__(
            message=message,
            code=901,
            user_info={'content': content})

class ResponseContentTypeNotValidException(TestingException):
    def __init__(self, content, expected_type, key_path):
        super(ResponseContentTypeNotValidException, self).__init__(
            message='The response content (%s):%s is not valid with type (%s) for key path: %s'
                    % (content, type(content), expected_type, key_path),
            code=902,
            user_info={'content': content,
                       'expected_type': expected_type,
                       'key_path': key_path})

class ResponseContentNotFoundException(TestingException):
    def __init__(self, key_path):
        assert isinstance(key_path, str)
        super(ResponseContentNotFoundException, self).__init__(
            message='The response not found with key path: %s' % key_path,
            code=903,
            user_info={})

class ResponseContentNotEqualException(TestingException):
    def __init__(self, key_path, response, expectation):
        assert isinstance(key_path, str)
        super(ResponseContentNotEqualException, self).__init__(
            message='The response content: %s is not equal to expectation: %s for key: %s'
                    % (response, expectation, key_path),
            code=904,
            user_info={})

class ResponseContentStatusNotMatchException(TestingException):
    def __init__(self, expected_code, response_code):
        assert isinstance(expected_code, int) and isinstance(response_code, int)
        super(ResponseContentStatusNotMatchException, self).__init__(
            message='The response status: %s is not equal to expectation: %s' % (response_code, expected_code),
            code=905,
            user_info={})