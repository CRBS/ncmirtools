#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_lookup
----------------------------------

Tests for `lookup` module.
"""
import re
import os
import sys
import tempfile
import shutil
import unittest
import argparse

from ncmirtools import ciluploader


class Parameters(object):
    """dummy"""
    pass

class TestCILUploader(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_arguments(self):

        help_formatter = argparse.RawDescriptionHelpFormatter
        parser = argparse.ArgumentParser(description='hi',
                                         formatter_class=help_formatter)
        subparsers = parser.add_subparsers(description='Command to run. ',
                                           dest='command')
        ciluploader.get_argument_parser(subparsers)

        pargs =  parser.parse_args(['cilupload', 'hi'])
        self.assertEqual(pargs.command, 'cilupload')
        self.assertEqual(pargs.data, 'hi')
        self.assertEqual(pargs.homedir, '~')

    def test_get_run_help_string(self):
        p = Parameters()
        p.program = 'hi'
        res = ciluploader._get_run_help_string(p)
        self.assertEqual(res, 'Please run hi -h for more information.')


if __name__ == '__main__':
    sys.exit(unittest.main())
