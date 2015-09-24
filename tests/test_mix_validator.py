__author__ = 'admin'

import os
from pre_commit_hook.validate import MixValidator
from unittest import TestCase


class TestMixValidator(TestCase):

    def test_read_line_with_tab(self):
        v = MixValidator()
        test_line = '123'
        valid, error = v._read_line(test_line)
        self.assertTrue(valid)
        self.assertIsNone(error)

        test_line = '\t 123'
        valid, error = v._read_line(test_line)
        self.assertFalse(valid)
        self.assertIsNotNone(error)

    def test_read_target_file(self):
        v = MixValidator()
        filename = 'order_2.apib'
        file_path = '%s/%s' % (os.getcwd(), filename)
        result, error = v.validate_file(file_path)
        self.assertFalse(result)
        self.assertIsNotNone(error)
        self.assertEqual('contains tab in line', error.message)
