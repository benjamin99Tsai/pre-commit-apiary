__author__ = 'admin'

from pre_commit_hook.apiary import _group_title
from pre_commit_hook.apiary import _api_title
from pre_commit_hook.apiary import _api_method
from pre_commit_hook.apiary import _api_url
from pre_commit_hook.apiary import _param_title
from pre_commit_hook.apiary import _param_string
from pre_commit_hook.apiary import _request_title
from pre_commit_hook.apiary import _response_title

from unittest import TestCase

# Define the testCase
class ApiaryPatternsTest(TestCase):

    def test_group_title(self):
        self.assertTrue(_group_title('# Group Test Number 1'))
        self.assertTrue(_group_title('# 123123'))
        self.assertFalse(_group_title('## false test'))
        self.assertFalse(_group_title(''))

    def test_api_title(self):
        self.assertTrue(_api_title('## Get the api [/test/api/pattern]'))
        self.assertTrue(_api_title('## api [/test/api/pattern{?withParameters}]'))
        self.assertTrue(_api_title('## api [/test/api/pattern/{withParameter}/test]'))
        self.assertFalse(_api_title('### Get the api [/test/api/pattern]'))
        self.assertFalse(_api_title('## api /test/api/pattern'))

    def test_api_method(self):
        self.assertTrue(_api_method('### api method [GET]'))
        self.assertTrue(_api_method('### api method [POST]'))
        self.assertTrue(_api_method('### api method [PUT]'))
        self.assertTrue(_api_method('### api method [DELETE]'))
        self.assertFalse(_api_method('### api method [NONE]'))
        self.assertTrue(_api_method('[POST]'))

    def test_api_url(self):
        self.assertEqual(_api_url('test [/test/api/url/pattern]').group(),
                         '[/test/api/url/pattern]')

        self.assertEqual(_api_url('test [/test/api/url/pattern{?withParameters,parameter2}').group(),
                         '[/test/api/url/pattern{')

        self.assertEqual(_api_url('test [/test/api/url/pattern/{parameter1}/and/{parameter2}').group(),
                         '[/test/api/url/pattern/{parameter1}/and/{')

        self.assertEqual(_api_url('test [/test/api/url/pattern/{parameter1}/and/{parameter2}{?test}').group(),
                         '[/test/api/url/pattern/{parameter1}/and/{')

    def test_param_title(self):
        self.assertTrue(_param_title('+ Parameters'))
        self.assertFalse(_param_title('- Parameters'))
        self.assertFalse(_param_title('+ Parameter'))

    def test_param_string(self):
        self.assertTrue(_param_string('    + test1       (string) ... descriptions'))
        self.assertTrue(_param_string('  + test2    (number) ... descriptions'))
        self.assertTrue(_param_string('+ test3   (boolean)'))
        self.assertTrue(_param_string('+ test4      (string, optional) ... descriptions'))

    def test_request_title(self):
        self.assertTrue(_request_title('+ Request IssueOrders(application/json)'))
        self.assertFalse(_request_title('+ Response 200 (application/json)'))
        self.assertFalse(_request_title('+ Parameters'))

    def test_response_title(self):
        self.assertTrue(_response_title('+ Response 200 (application/json)'))
        self.assertTrue(_response_title('+ Response 400 (application/json)'))
        self.assertTrue(_response_title('+ Response 300'))
        self.assertTrue(_response_title('+ Response'))
        self.assertFalse(_response_title('+ Request'))
        self.assertFalse(_response_title('+ Parameters'))