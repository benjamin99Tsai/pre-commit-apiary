__author__ = 'admin'

DEBUG=False

if __name__ == '__main__':
    import sys, os
    sys.path.append('%s/../../' % os.path.dirname(os.path.realpath(__file__)))

import re
import six
from abc import ABCMeta, abstractmethod
from pre_commit_hook.api.ApiContentElement import ApiContentElement, ApiContentElementFactory
from pre_commit_hook.api.ApiContentElement import ApiContentStringElement, ApiContentNumberElement, ApiContentBooleanElement
from pre_commit_hook.api.ApiContentElement import ApiContentArrayElement, ApiContentDictionaryElement
from pre_commit_hook.api.Exception import ApiParsingException

RE_FLAGS = re.VERBOSE|re.MULTILINE|re.DOTALL

WHITESPACE          = re.compile(r'[ \t]+', re.MULTILINE)
WHITESPACE_STRING   = ' \t'
NEWLINE_STRING      = '\r\n'
_white_search       = WHITESPACE.search
_url_pattern        = re.compile(r'http[s]*\/\/:[\w\_\-\.a-zA-Z0-9]+}').match


__all__ = ['ApiDecoder']


def _get_api_response_element_from_element_and_comment(element, comment):
    if comment is None:
        return _get_api_response_element_from_element(element)
    else:
        assert isinstance(comment, ApiDecoder.ApiComment)
        if 'type' in comment:
            assert _validate_element_with_string_type(element, comment.get('type')), \
                'The type defined in comment does not match.'
            api_response_element = ApiContentElementFactory.get_response_element_by_type(comment.get('type'))
        else:
            api_response_element = _get_api_response_element_from_element(element)

        assert comment.get('required', None) is not None, 'Process error: getting comment without required tag'
        api_response_element.required = comment.get('required')

        return api_response_element

def _get_api_response_element_from_element(element):
    """
    >>> d = ApiDecoder()
    >>> isinstance(_get_api_response_element_from_element('string element'), ApiContentStringElement)
    True
    >>> isinstance(_get_api_response_element_from_element(123123.0), ApiContentNumberElement)
    True
    >>> isinstance(_get_api_response_element_from_element(False), ApiContentBooleanElement)
    True
    """
    if isinstance(element, str):
        return ApiContentElementFactory.get_response_element_by_type('string')
    elif isinstance(element, bool):
        element = ApiContentElementFactory.get_response_element_by_type('boolean')
        return element
    elif isinstance(element, float) or isinstance(element, int):
        return ApiContentElementFactory.get_response_element_by_type('number')

    raise ApiParsingException(
        message="input element type(%s) does not match any ApiResponseElement" % type(element)
    )

def _validate_element_with_string_type(element, string_type):
    valid = True
    string_type = string_type.lower()
    if string_type == 'string' or string_type == ApiContentElement.Type.url.name:
        valid = isinstance(element, str)
    elif string_type == ApiContentElement.Type.number.name or string_type == ApiContentElement.Type.timestamp.name:
        valid = isinstance(element, float) or isinstance(element, int)
    elif string_type == ApiContentElement.Type.boolean.name:
        valid = isinstance(element, bool)
    elif string_type == ApiContentElement.Type.url.name:
        valid = isinstance(element, str) and _url_pattern(element)
    else:
        raise ApiParsingException(
            message='Input string_type(%s) is not valid.' % string_type
        )

    return valid


# ----------------------------------------------------------------------------------------------------------------------
#  The (JSON)-like Objects for Decoder
# ----------------------------------------------------------------------------------------------------------------------
@six.add_metaclass(ABCMeta)
class ApiBaseObject(object):
    _BASE_CLS = object

    def __init__(self):
        self.previous_element_append_with_comma = False
        self._base_element = self.__class__._BASE_CLS()
        self._key = None
        self._duplication_reference = None
        self._base_element.required = True

    def __eq__(self, other):
        assert isinstance(other, ApiBaseObject)
        return self._base_element == other._base_element

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def append_child(self, child, key=None):
        pass

    def set_required(self, required):
        assert isinstance(required, bool)
        self._base_element.required = required

    def set_duplication_reference(self, reference):
        self._duplication_reference = reference

    def get_duplication_reference(self):
        return self._duplication_reference

    def get_base_element(self):
        return self._base_element

    def get_key(self):
        return self._key

class ApiDictionaryObject(ApiBaseObject):
    """
        # For doctest:
        >>> object = ApiDictionaryObject()
        >>> object.append_child('Alice', key='name')
        >>> object.append_child(_get_api_response_element_from_element(25), key='age')
        >>> isinstance(object.get('name'), ApiContentStringElement)
        True
        >>> isinstance(object["age"], ApiContentNumberElement)
        True
    """
    _BASE_CLS = ApiContentDictionaryElement

    def append_child(self, child, key=None):
        if not isinstance(child, ApiContentElement):
            child = _get_api_response_element_from_element(child)
        assert key is not None
        self[key] = child

    def get(self, key, default=None):
        assert isinstance(key, str), "The key should be a string instead of type: %s." % type(key)
        if key not in self._base_element:
            return default
        else:
            return self._base_element[key]

    def __setitem__(self, key, value):
        assert isinstance(key, str), "The key should be a string instead of type: %s." % type(key)
        self._base_element[key] = value

    def __getitem__(self, key):
        assert isinstance(key, str), "The key should be a string instead of type: %s." % type(key)
        return self._base_element.get(key, None)

    def __len__(self):
        return len(self._base_element)

class ApiArrayObject(ApiBaseObject):
    """
        # For doctest:
        >>> array_object = ApiArrayObject()
        >>> array_object.append_child(999)
        >>> array_object.append_child(10)
        >>> isinstance(array_object[0], ApiContentNumberElement)
        True
        >>> d1 = ApiContentDictionaryElement()
        >>> d2 = ApiContentDictionaryElement()
        >>> name = ApiContentStringElement()
        >>> name.required = True
        >>> age = ApiContentNumberElement()
        >>> age.required = True
        >>> title = ApiContentStringElement()
        >>> title.required = False
        >>> code = ApiContentNumberElement()
        >>> code.required = False
        >>> d1.add_element(name, 'name')
        >>> d2.add_element(name, 'name')
        >>> d1.add_element(age, 'age')
        >>> d2.add_element(age, 'age')
        >>> d1.add_element(title, 'title')
        >>> d2.add_element(code, 'code')
        >>> array = ApiContentArrayElement()
        >>> array.add_element(d1)
        >>> array.add_element(d2)
        >>> element = array[0]
        >>> isinstance(element['name'], ApiContentStringElement)
        True
        >>> isinstance(element['age'], ApiContentNumberElement)
        True
        >>> isinstance(element['title'], ApiContentStringElement)
        True
        >>> isinstance(element['code'], ApiContentNumberElement)
        True
    """
    _BASE_CLS = ApiContentArrayElement


    # Override the set_duplication_reference:
    def set_duplication_reference(self, reference):
        super(ApiArrayObject, self).set_duplication_reference(reference)
        self.append_child(reference)

    def append_child(self, child, key=None):
        if not isinstance(child, ApiContentElement):
            child = _get_api_response_element_from_element(child)
        self._base_element.add_element(child)

    def __getitem__(self, index):
        assert isinstance(index, int), "The index should be an int instead of type: %s" % type(index)
        assert (not index < 0) and (index < len(self._base_element)), "Index range out of bound"
        return self._base_element[index]

    def __len__(self):
        return len(self._base_element)

# ----------------------------------------------------------------------------------------------------------------------
#  The Decoder:
# ----------------------------------------------------------------------------------------------------------------------
class ApiDecoder(object):
    _str_search      = re.compile(r'\"[\b@\b%\w\_\-\.\s,\:\/\[\]\(\)\{\}\~\<\>\&\+\\]*\"', re.UNICODE).search
    _comment_tag     = re.compile(r'\/\/').search
    _url_search      = re.compile(r'(http(s)*:)\/\/').search
    _comment_search  = re.compile(r'\[[a-zA-Z\s\w\_\-\.0-9,\(\)]*\]').search
    _subtype_search  = re.compile(r'\([a-zA-Z\_\-\. 0-9]+\)').search
    _number_match    = re.compile(r'[1-9][0-9]*(.[0-9]+)?').match

    # The object for handling comment info:
    class ApiComment(object):
        def __init__(self):
            self._info = dict()

        def __contains__(self, key):
            assert isinstance(key, str)
            return key in self._info

        def __getitem__(self, key, default=None):
            assert isinstance(key, str)
            return self._info.get(key, default)

        def __setitem__(self, key, value):
            assert isinstance(key, str)
            self._info[key] = value

        def get(self, key, default=None):
            return self._info.get(key, default)

    def __init__(self):
        self._object_stacks        = list()    # The stack for the parsing process
        self._parsed_objects       = None      # The parsed result(s)
        self._buffered_element     = None
        self._line_scanned_comment = None

    # Comment Related: -------------------------------------------------------------------------------------------------
    def _get_comment_string(self, line):
        """
        >>> d = ApiDecoder()
        >>> d._get_comment_string('this is the test message without any comment')
        (None, 'this is the test message without any comment')
        >>> d._get_comment_string('this is the test message // comment message')
        (' comment message', 'this is the test message ')
        >>> d._get_comment_string('this is the test message with url: https://test.url.path // comment message here')
        (' comment message here', 'this is the test message with url: https://test.url.path ')
        >>> d._get_comment_string('"url1": "http://123.321", "url2": "https://test.url.path" // comment message')
        (' comment message', '"url1": "http://123.321", "url2": "https://test.url.path" ')
        >>> d._get_comment_string('message // comment message with url: https://test.url.path')
        (' comment message with url: https://test.url.path', 'message ')
        """
        comment_tag = self._comment_tag(line)
        if not comment_tag:
            return None, line

        # Check if the '//' sign comes from the 'https://'
        url = self._url_search(line)
        if url is not None:
            if url.end() == comment_tag.end():
                comment_string, reminder = self._get_comment_string(line[comment_tag.end():])
                return comment_string, line[:comment_tag.end()] + reminder

        return line[comment_tag.end():], line[:comment_tag.end()-2]

    def _parse_comment(self, comment):
        """
        >>> d = ApiDecoder()
        >>> d._parse_comment('this is the test comment. [string, optional]').get('type')
        'string'
        >>> d._parse_comment('this is the test comment. [string, optional]').get('required')
        False
        >>> d._parse_comment('this is the test comment. [optional]').get('required')
        False
        >>> d._parse_comment_info('number(timestamp)').get('type')
        'timestamp'
        >>> d._parse_comment_info('number(timestamp)').get('required')
        True
        >>> d._parse_comment('this is the null comment.') # should get None, i.e. nothing
        >>> d._parse_comment('test for complex comment: // [string(url), optional]').get('type')
        'url'
        >>> d._parse_comment('test for complex comment: // [string(url), optional]').get('required')
        False
        """
        info = self._comment_search(comment)
        if info:
            return self._parse_comment_info(comment[info.start()+1:info.end()-1])
        else:
            return None

    def _parse_comment_info(self, info):
        buffer  = ''
        index   = 0
        result  = ApiDecoder.ApiComment()
        while True:
            next_chart = info[index]
            # skip whitespaces:
            if next_chart in WHITESPACE_STRING:
                index  = _white_search(info).end()
                buffer = ''
                continue
            # reach the end of the info
            elif index == len(info)-1:
                buffer += info[index]
                self._save_content_info_into_comment(buffer, result)
                break
            # reach the end of one content in the info:
            elif next_chart == ',':
                self._save_content_info_into_comment(buffer, result)
                buffer = '' # reset the buffer
            else:
                buffer += info[index]

            index += 1

        # check for the 'required' flag:
        if 'required' not in result and 'type' in result:
            result['required'] = True

        return result

    def _save_content_info_into_comment(self, content_info, comment):
        if content_info == 'optional':
            comment['required'] = False
        elif content_info == 'required':
            comment['required'] = True
        elif content_info == 'duplicate':
            comment['duplication'] = True
        else:
            if 'type' in comment:
                raise ApiParsingException(
                    message='Comment Syntax Error: could only specify one type in the comment.'
                )

            search = self._subtype_search(content_info)
            if search:
                comment['type'] = content_info[search.start()+1:search.end()-1]
            else:
                comment['type'] = content_info

    def _get_line_scanned_comment(self):
        if self._line_scanned_comment:
            comment = self._line_scanned_comment
            self._line_scanned_comment = None
            return comment
        else:
            return None

    def _set_line_scanned_comment(self, comment):
        assert self._line_scanned_comment is None and isinstance(comment, ApiDecoder.ApiComment)
        self._line_scanned_comment = comment

    # Parsing Related --------------------------------------------------------------------------------------------------
    def _parse_string(self, string):
        """
        # For the doctest:
        >>> d = ApiDecoder()
        >>> d._parse_string('\"123ZZ\": 321')
        ('123ZZ', 7)
        >>> d._parse_string('\"AAA ZZZ_QQ123\" \"AAZZ\"')
        ('AAA ZZZ_QQ123', 15)
        """
        search = self._str_search(string)
        assert search is not None, "The input string does not match the pattern"
        if search is None:
            raise ApiParsingException(
                message='The input content does not match the string pattern.'
            )
        return string[1:search.end() - 1], search.end()

    # Main scanning operation function ---------------------------------------------------------------------------------
    def scan_line(self, line):
        # Parse the comments:
        comment_string, line = self._get_comment_string(line)
        if comment_string:
            comment = self._parse_comment(comment_string)
            if comment:
                self._set_line_scanned_comment(comment)

        # Skip the whitespaces:
        index = 0
        while index < len(line):
            next_chart = line[index]
            if next_chart in WHITESPACE_STRING:
                index += _white_search(line[index:]).end()
                if index == len(line):
                    self._append_buffered_element_to_current_object()
                continue

            elif next_chart == "{":
                new_object = self._create_dictionary_object_with_comment(self._get_line_scanned_comment())
                self._append_object_to_stack(new_object)

            elif next_chart == "}":
                if not isinstance(self._get_current_object(), ApiDictionaryObject):
                    raise ApiParsingException(message='expected to be a dictionary object with line: %s' % line)
                self._pop_and_save_object()

            elif next_chart == "[":
                new_object = self._create_array_object_with_comment(self._get_line_scanned_comment())
                self._append_object_to_stack(new_object)

            elif next_chart == "]":
                if not isinstance(self._get_current_object(), ApiArrayObject):
                    raise ApiParsingException(message='expected to be an array object with line: %s' % line)
                self._pop_and_save_object()

            elif next_chart == "\"":
                string, length = self._parse_string(line[index:])
                self._save_buffered_element(string)
                index += length
                continue

            elif next_chart == ":":
                if not isinstance(self._buffered_element, str):
                    raise ApiParsingException(message='expected to be a string object before the \":\" sign')
                key = self._buffered_element
                self._buffered_element = dict(key=key)

            elif next_chart == 'T' or next_chart == 't':
                buffer = line[index:index + 4]
                if not buffer.lower() == 'true':
                    raise ApiParsingException(message='could not recognize the syntax: %s' % buffer)
                self._save_buffered_element(bool(True))
                index += 4
                continue

            elif next_chart == 'F' or next_chart == 'f':
                buffer = line[index:index + 5]
                if not buffer.lower() == 'false':
                    raise ApiParsingException(message='could not recognize the syntax: %s' % buffer)
                self._save_buffered_element(bool(False))
                index += 5
                continue

            elif re.match(r'[1-9]', next_chart):
                number_match = self._number_match(line[index:])
                index += number_match.end()
                self._save_buffered_element(float(number_match.group()))
                continue

            elif re.match(r'0', next_chart):
                self._save_buffered_element(float(next_chart))

            elif next_chart == ".":
                buffer = line[index:index + 3]
                if not buffer == '...':
                    raise ApiParsingException(message='could not recognize the syntax: %s' % buffer)
                index += 3
                self._get_current_object().previous_element_append_with_comma = False
                continue

            elif next_chart == ",":
                self._append_buffered_element_to_current_object(append_with_comma=True)

            elif next_chart in NEWLINE_STRING or index == len(line)-1:
                self._append_buffered_element_to_current_object()

            else:
                raise ApiParsingException(message='Syntax Error with line: %s' % line)

            index += 1

        # Combine the object with the comments:

    # Append element Related: ------------------------------------------------------------------------------------------
    def _save_buffered_element(self, element):
        if isinstance(self._buffered_element, dict):
            assert ('value' not in  self._buffered_element and 'key' in self._buffered_element), \
                'the dictionary element had not been properly processed'
            self._buffered_element['value'] = element
        else:
            self._buffered_element = element

    def _append_buffered_element_to_current_object(self,
                                                   append_with_comma=False,
                                                   append_before_saving_the_container=False):
        if self._buffered_element is None:
            if append_with_comma:
                self._get_current_object().previous_element_append_with_comma = append_with_comma
            return

        current_object = self._get_current_object()
        assert current_object is not None
        if not append_before_saving_the_container \
                and not self._get_current_object().previous_element_append_with_comma \
                and len(current_object):
            raise ApiParsingException(message='The previous element should ended with comma')

        self._get_current_object().previous_element_append_with_comma = append_with_comma
        if isinstance(self._buffered_element, dict):
            if not isinstance(current_object, ApiDictionaryObject):
                raise ApiParsingException(message='the object type and the current element(s) does not match')
            element = self._buffered_element['value']
            comment = self._get_line_scanned_comment()
            api_response_element = _get_api_response_element_from_element_and_comment(element, comment)
            current_object.append_child(api_response_element, self._buffered_element['key'])
        else:
            if not isinstance(current_object, ApiArrayObject):
                raise ApiParsingException(message='the object type and the current element(s) does not match')
            element = self._buffered_element
            comment = self._get_line_scanned_comment()
            api_response_element = _get_api_response_element_from_element_and_comment(element, comment)
            current_object.append_child(api_response_element)

        # Clear the buffered element:
        self._buffered_element = None

    # Object Stack Related: --------------------------------------------------------------------------------------------
    def _get_current_object(self):
        current_object = None
        if len(self._object_stacks):
            current_object = self._object_stacks[-1]
        return current_object

    def _create_array_object_with_comment(self, comment):
        return self._create_object_with_comment(comment, target_object=ApiArrayObject)

    def _create_dictionary_object_with_comment(self, comment):
        return self._create_object_with_comment(comment, target_object=ApiDictionaryObject)

    def _create_object_with_comment(self, comment, target_object):
        new_object = target_object()
        if comment:
            assert isinstance(comment, ApiDecoder.ApiComment)
            if 'duplication' in comment:
                assert len(self._object_stacks), 'Syntax error with the duplication tag'
                new_object.set_duplication_reference(self._get_duplication_reference())
            new_object.set_required(comment['required'])
        return new_object

    def _get_duplication_reference(self):
        current_object = self._get_current_object()
        assert isinstance(current_object, ApiDictionaryObject), 'Syntax Error with duplication tag'
        return current_object.get_base_element().copy()

    def _append_object_to_stack(self, new_object):
        assert isinstance(new_object, ApiBaseObject), "The input object should be an ApiBaseObject Type"
        if isinstance(self._buffered_element, dict):
            new_object._key = self._buffered_element['key']
            self._buffered_element = None
        self._object_stacks.append(new_object)

    def _pop_and_save_object(self):
        if self._get_current_object().previous_element_append_with_comma:
            raise ApiParsingException(message='The last element in the container should not end with comma')

        self._append_buffered_element_to_current_object(append_before_saving_the_container=True)
        content_object   = self._object_stacks.pop(-1)
        container_object = self._get_current_object()
        if container_object is not None:
            if len(container_object) \
                    and not container_object.get_duplication_reference() \
                    and not container_object.previous_element_append_with_comma:
                raise ApiParsingException(message='The previous element in the container should ended with comma')

            container_object.previous_element_append_with_comma = False
            if isinstance(container_object, ApiDictionaryObject):
                if content_object.get_key() is None:
                    raise ApiParsingException(message='Cannot find the key for the dictionary element')
                container_object.append_child(content_object.get_base_element(), content_object.get_key())
            else:
                assert content_object.get_key() is None
                container_object.append_child(content_object.get_base_element())
        else:
            self._parsed_objects = content_object.get_base_element()

    def get_parsed_objects(self):
        return self._parsed_objects

    def clear(self):
        self._parsed_objects = None
        self._object_stacks.clear()


if __name__ == "__main__":
    # Running the doctest:
    # import doctest
    # doctest.testmod()

    from os import path
    my_path = path.dirname(path.abspath(__file__))
    with open('%s/../tests/response/response_error_example005.json' % my_path, 'r') as file:
        lines = file.readlines()

    decoder = ApiDecoder()
    line_count = 0
    for line in lines:
        line_count += 1
        print('%d %s' % (line_count, line))
        decoder.scan_line(line)
    print('\nResults: \n%s' % decoder.get_parsed_objects())