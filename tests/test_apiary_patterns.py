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

# Utilities:
def _print_test_title(title):
        print('ApiaryPatternsTest: test %s', title)

# Define the testCase
class ApiaryPatternsTest(TestCase):

    def test_group_title(self):
        _print_test_title('pattern group title')
        self.assertTrue(_group_title('# Group Test Number 1'))
        self.assertTrue(_group_title('# 123123'))
        self.assertFalse(_group_title('## false test'))
        self.assertFalse(_group_title(''))

    def test_api_title(self):
        print('')

