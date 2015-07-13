__author__ = 'admin'

DEBUG=True

if __name__ == '__main__':
    import sys, os
    sys.path.append('%s/../' % os.path.dirname(os.path.realpath(__file__)))

from abc import ABCMeta, abstractclassmethod, abstractmethod
from pre_commit_hook.api.Exception import ResponseContentTypeNotValidException, ResponseContentNotFoundException
from enum import Enum
import re
import random
import string
import six

# --------------------------------------------------------------------------------------
# The Abstract Class for Api Response Element
# --------------------------------------------------------------------------------------
@six.add_metaclass(ABCMeta)
class ApiContentElement(object):
    class Type(Enum):
        array       = 0
        dictionary  = 1
        string      = 2
        url         = 3
        number      = 4
        timestamp   = 5
        boolean     = 6
        duplicate   = 7

    content  = None
    default  = None
    type     = None
    required = True

    def __init__(self, type):
        assert isinstance(type, ApiContentElement.Type), "The type of the element should be ApiResponseElement.Type"
        self.required   = True
        self.type       = type
        self._parent    = None # for fetching the key_path

    def __str__(self):
        return self._get_description()

    def __eq__(self, other):
        return self.type == other.type

    def _get_description(self, indents=0):
        return "(%s, required: %s)" % (self.type.name, self.required)

    @staticmethod
    def _get_indents_string(indents):
        assert isinstance(indents, int), "The indents should be an integer"
        indents_string = ""
        for i in range(0, indents):
            indents_string = "\t" + indents_string
        return indents_string

    def set_default_value(self, value):
        assert isinstance(value, str), "The input value should be a string type"
        assert self.__class__.validate_with_value(value), \
            "The input string format is not compatible to the element type"
        self.default = value

    def set_parent(self, parent):
        assert isinstance(parent, ApiContentSetElement), 'The parent can only be an array or a dictionary'
        self._parent = parent

    def get_key_path(self):
        if self._parent:
            return self._parent.get_key_path_with_element(element=self)
        return None

    @abstractclassmethod
    def generate_json_object(self):
        return None

    @abstractclassmethod
    def validate_json_object(self, json_object):
        pass



# --------------------------------------------------------------------------------------
# The Class for Special Response Element Type (Duplicate):
# --------------------------------------------------------------------------------------
class ApiContentDuplicateElement(ApiContentElement):
    def __init__(self, source_element):
        assert isinstance(source_element, ApiContentElement), "The duplicate source should be an ApiResponseElement"
        self.source_element = source_element
        super(ApiContentDuplicateElement, self).__init__(source_element.type)

    def generate_json_object(self):
        return self.source_element.generate_json_object()

    def validate_json_object(self, json_object):
        return self.source_element.validate_json_object(json_object)

    def _get_required_keys(self):
        if hasattr(self.source_element, '_get_required_keys'):
            return self.source_element._get_required_keys()
        else:
            return list()


# --------------------------------------------------------------------------------------
# The Class for String Value Element:
# --------------------------------------------------------------------------------------
class ApiContentStringElement(ApiContentElement):
    def __init__(self, type=None):
        if not type:
            type = ApiContentElement.Type.string
        super(ApiContentStringElement, self).__init__(type)

    def generate_json_object(self):
        samples = string.ascii_lowercase + string.ascii_uppercase + string.digits
        length  = random.randint(2,32)
        result  = ''.join(random.sample(samples, length))
        return result

    def validate_json_object(self, json_object):
        if not isinstance(json_object, str):
            raise ResponseContentTypeNotValidException(
                json_object,
                self.type.name,
                self.get_key_path())


# --------------------------------------------------------------------------------------
# The Class for URL Value Element:
# --------------------------------------------------------------------------------------
class ApiContentUrlElement(ApiContentStringElement):
    def __init__(self):
        super(ApiContentUrlElement, self).__init__(ApiContentElement.Type.url)

    def generate_json_object(self):
        samples = string.ascii_lowercase + string.ascii_uppercase + string.digits
        url_string = 'https://'
        section_count = random.randint(1,8)
        for i in range(section_count):
            length = random.randint(1,16)
            url_string = '%s%s/' % (url_string, ''.join(random.sample(samples, length)))
        if random.randint(0,1) == 1:
            url_string = url_string[:len(url_string)-1]

        return url_string

    def validate_json_object(self, json_object):
        assert isinstance(json_object, str)
        url_pattern = '^http(s)*:\/(\/[a-zA-Z0-9|_|-|\?|\.|=]*)+(\/)*$'
        return re.match(url_pattern, json_object)

# --------------------------------------------------------------------------------------
# The Class for Number Value Element:
# --------------------------------------------------------------------------------------
class ApiContentNumberElement(ApiContentElement):
    def __init__(self, type=None):
        if not type:
            type = ApiContentElement.Type.number
        super(ApiContentNumberElement, self).__init__(type)

    def generate_json_object(self):
        return random.randint(-9999, 9999)

    def validate_json_object(self, json_object):
        if not isinstance(json_object, int) and not isinstance(json_object, float):
            raise ResponseContentTypeNotValidException(
                json_object,
                self.type.name,
                self.get_key_path())


# --------------------------------------------------------------------------------------
# The Class for Timestamp Value Element:
# --------------------------------------------------------------------------------------
class ApiContentTimestampElement(ApiContentNumberElement):
    def __init__(self):
        super(ApiContentTimestampElement, self).__init__(ApiContentElement.Type.timestamp)

    def generate_json_object(self):
        import time
        return int(time.time())

    def validate_json_object(self, json_object):
        return isinstance(json_object, int) or isinstance(json_object, float)

# --------------------------------------------------------------------------------------
# The Class for Boolean Value Element:
# --------------------------------------------------------------------------------------
class ApiContentBooleanElement(ApiContentElement):
    def __init__(self):
        super(ApiContentBooleanElement, self).__init__(ApiContentElement.Type.boolean)

    def set_default_value(self, value):
        ApiContentBooleanElement.validate_with_value(value)
        true_pattern = r'^(true|y|t)$'
        self.default = re.match(true_pattern, value) is not None

    def generate_json_object(self):
        return random.randint(0, 1) == 1

    def validate_json_object(self, json_object):
        if not isinstance(json_object, bool):
            raise ResponseContentTypeNotValidException(
                json_object,
                self.type.name,
                self.get_key_path())

# --------------------------------------------------------------------------------------
# The Base Class for Set Element:
# --------------------------------------------------------------------------------------
@six.add_metaclass(ABCMeta)
class ApiContentSetElement(ApiContentElement):
    def __init__(self, type):
        super(ApiContentSetElement, self).__init__(type)

    @abstractclassmethod
    def __eq__(self, other):
        # Should re-define the equality for the SetElement
        return False

    @abstractclassmethod
    def _get_description(self, indents=0):
        return None

    @abstractclassmethod
    def add_element(self, element, key=None):
        # Validate the input key/element
        if key is not None:
            assert isinstance(key, str), "The key should be a string value"
        assert isinstance(element, ApiContentElement), "The input element should be an ApiResponseElement"

    @abstractclassmethod
    def copy(self):
        return None

    @abstractmethod
    def get_key_path_with_element(self):
        return None

# --------------------------------------------------------------------------------------
# The Class for Array Value Element:
# --------------------------------------------------------------------------------------
class ApiContentArrayElement(ApiContentSetElement):
    def __init__(self):
        super(ApiContentArrayElement, self).__init__(ApiContentElement.Type.array)
        self.content = list()

    def __eq__(self, other):
        if self.type != other.type:
            return False

        for my_element in self.content:
            found_matched = False
            for others_element in other.content:
                if my_element == others_element:
                    found_matched = True
                    break
            if not found_matched:
                return False

        for others_element in other.content:
            found_matched = False
            for my_element in self.content:
                if my_element == others_element:
                    found_matched = True
                    break
            if not found_matched:
                return False
        return True

    def __getitem__(self, index):
        assert isinstance(index, int) and index < len(self.content)
        return self.content[index]

    def __contains__(self, item):
        return item in self.content

    def __len__(self):
        return len(self.content)

    def copy(self):
        copy_element = ApiContentArrayElement()
        copy_element.type = self.type
        copy_element.default = self.default
        copy_element.required = self.required
        copy_element = self.content[:]
        return copy_element

    def _get_description(self, indents=0):
        indent_string = ApiContentElement._get_indents_string(indents)
        description = "%s[" % indent_string
        for element in self.content:
            description += "\n%s\t%s," % \
                      (indent_string, element._get_description(indents+1))
        description = description[:len(description)-1] + "\n%s]" % indent_string  # Omit the last ','
        return description

    def get_key_path_with_element(self, element):
        assert isinstance(element, ApiContentElement), 'The input element should be an ApiResponseElement'
        key_path = None
        for index in range(len(self.content)):
            if id(self[index]) == id(element):
                key_path = '%d' % index
                break
        assert key_path, 'Error: could not found the corresponding element'

        parent_key_path = self.get_key_path()
        if parent_key_path:
            key_path = '%s.%s' % (parent_key_path, key_path)

        return key_path

    def add_element(self, element, key=None):
        super(ApiContentArrayElement, self).add_element(element)
        # If already have one element in the list, first check if they are the same, and than merge both elements
        if len(self.content):
            original = self.content.pop()
            assert element == original, 'Syntax Error: trying to add element to the Array which is not match'
            if isinstance(element, ApiContentDictionaryElement):
                element.merge(original)
        self.content.append(element)
        element.set_parent(self)

    def generate_json_object(self):
        json_object = list()
        for element in self.content:
            json_object.append(element.generate_json_object())
        return json_object

    def validate_json_object(self, json_object):
        if not isinstance(json_object, list):
            raise ResponseContentTypeNotValidException(
                json_object,
                self.type.name,
                self.get_key_path())

        for i in range(0, len(json_object)):
            content_index = i
            if not content_index < len(self.content):
                content_index = 0 # TODO: find the proper index for the self.content
            self.content[content_index].validate_json_object(json_object[i])

# --------------------------------------------------------------------------------------
# The Class for Dictionary Value Element:
# --------------------------------------------------------------------------------------
class ApiContentDictionaryElement(ApiContentSetElement):
    def __init__(self):
        super(ApiContentDictionaryElement, self).__init__(ApiContentElement.Type.dictionary)
        self.content = dict()

    def __eq__(self, other):
        # validate if the types are the same:
        if self.type != other.type:
            if DEBUG:
                print('DEBUG for __eq__: types not matched')
            return False

        # validate if the required keys are the same:
        self_required_keys  = self._get_required_keys()
        other_required_keys = other._get_required_keys()
        if not self_required_keys == other_required_keys:
            if DEBUG:
                print('DEBUG for __eq__: required keys not matched\n self: %s\n other: %s'
                      % (self_required_keys, other_required_keys))
            return False
        # validate the values:
        for key in self_required_keys:
            if not self.content.get(key) == other.content.get(key):
                print('DEBUG for __eq__: values not match for key: %s\n self: %s\n other: %s'
                      % (key, self.content.get(key), other.content.get(key)))
                return False

        return True

    def __getitem__(self, key):
        assert isinstance(key, str)
        return self.content[key]

    def __setitem__(self, key, element):
        assert isinstance(key, str)
        self.add_element(element, key)

    def __contains__(self, key):
        assert isinstance(key, str)
        return key in self.content.keys()

    def copy(self):
        copy_element = ApiContentDictionaryElement()
        copy_element.type = self.type
        copy_element.default = self.default
        copy_element.required = self.required
        copy_element.content = self.content.copy()
        return copy_element

    def merge(self, other):
        assert isinstance(other, ApiContentDictionaryElement), 'Could only merge with ApiResponseDictionaryElement'
        for key in other.content:
            if key not in self:
                assert not other.get(key).required, 'Syntax Error with duplication conflict'
                self[key] = other.get(key)

    def get(self, key, default=None):
        return self.content.get(key, default)

    def _get_required_keys(self):
        required_keys = list()
        for key in self.content:
            if self.content.get(key).required:
                required_keys.append(key)
        required_keys.sort()
        return required_keys

    def _get_description(self, indents=0):
        indent_string = ApiContentElement._get_indents_string(indents)
        string = "%s{" % indent_string
        for key in self.content:
            string += "\n%s\t%s: %s," % \
                      (indent_string, key, self.content[key]._get_description(indents+1))

        string = string[:len(string)-1] + "\n%s}" % indent_string # Omit the last ','
        return string

    def add_element(self, element, key=None):
        assert key is not None
        super(ApiContentDictionaryElement, self).add_element(element, key)
        self.content[key] = element
        element.set_parent(self)

    def get_key_path_with_element(self, element):
        assert isinstance(element, ApiContentElement), 'The input element should be an ApiResponseElement'
        key_path = None
        for key in self.content:
            if id(self.content.get(key)) == id(element):
                key_path = '%s' % key
                break
        assert key_path, 'Error: could not found the corresponding element'

        parent_key_path = self.get_key_path()
        if parent_key_path:
            key_path = '%s.%s' % (parent_key_path, key_path)

        return key_path

    def generate_json_object(self):
        json_object = dict()
        for key in self.content:
            element = self.content[key]
            if element.required:
                json_object[key] = element.generate_json_object()
            elif bool(random.getrandbits(1)):
                json_object[key] = element.generate_json_object()

        return json_object

    def validate_json_object(self, json_object):
        if not isinstance(json_object, dict):
            raise ResponseContentTypeNotValidException(
                json_object,
                self.type,
                self.get_key_path())

        for key in self.content:
            element   = self.content.get(key)
            js_object = json_object.get(key, None)
            if js_object is None and element.required:
                key_path = '%s.%s' % (self.get_key_path(), key)
                raise ResponseContentNotFoundException(key_path)
            if js_object:
                self.content[key].validate_json_object(js_object)

# --------------------------------------------------------------------------------------
# The Factory Class for the ApiResponseElement
# --------------------------------------------------------------------------------------
class ApiContentElementFactory(object):
    _element_table = {
        # TODO: should define for more element type
        ApiContentElement.Type.string.name:        ApiContentStringElement,
        ApiContentElement.Type.url.name:           ApiContentUrlElement,
        ApiContentElement.Type.number.name:        ApiContentNumberElement,
        ApiContentElement.Type.boolean.name:       ApiContentBooleanElement,
        ApiContentElement.Type.timestamp.name:     ApiContentTimestampElement,
        ApiContentElement.Type.dictionary.name:    ApiContentDictionaryElement,
        ApiContentElement.Type.array.name:         ApiContentArrayElement,
    }

    @classmethod
    def get_response_element_by_type(cls, type_string):
        '''
        # For the doctest:
        >>> string_a    = ApiContentElementFactory.get_response_element_by_type('string')
        >>> number_a    = ApiContentElementFactory.get_response_element_by_type('number')
        >>> boolean_a   = ApiContentElementFactory.get_response_element_by_type('boolean')
        >>> array_a     = ApiContentElementFactory.get_response_element_by_type('array')
        >>> dict_a      = ApiContentElementFactory.get_response_element_by_type('dictionary')
        >>> isinstance(string_a, ApiContentStringElement)
        True
        >>> isinstance(number_a, ApiContentNumberElement)
        True
        >>> isinstance(boolean_a, ApiContentBooleanElement)
        True
        >>> isinstance(array_a, ApiContentArrayElement)
        True
        >>> isinstance(dict_a, ApiContentDictionaryElement)
        True
        >>> string_a = ApiContentElementFactory.get_response_element_by_type('string')
        >>> string_b = ApiContentElementFactory.get_response_element_by_type('string')
        >>> id(string_a) == id(string_b)
        False
        '''
        assert isinstance(type_string, str), "The input type index should be a string"
        assert type_string in ApiContentElementFactory._element_table, \
            "The request element type: %s is not defined" % type_string
        element = ApiContentElementFactory._element_table[type_string]()
        element.required = True
        return element

    @classmethod
    def is_revolved_type_valid_with_expected_type(cls, resolved_type_string, expected_type_string):
        assert isinstance(resolved_type_string, str) and (expected_type_string, str)
        return issubclass(
            type(cls.get_response_element_by_type(expected_type_string)),
            type(cls.get_response_element_by_type(resolved_type_string))
        )



if __name__ == '__main__':

    # Running the doctest:
    import doctest
    doctest.testmod()