#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_lookup
----------------------------------

Tests for `lookup` module.
"""
import sys
import unittest

from ncmirtools import ncmirtool


class TestNcmirTool(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_arguments(self):
        pargs = ncmirtool._parse_arguments('desc',
                                           ['cilupload', 'hi'])
        self.assertEqual(pargs.command, 'cilupload')
        self.assertEqual(pargs.loglevel, 'WARNING')
        self.assertEqual(pargs.data, 'hi')

    def test_main_no_matching_command(self):
        res = ncmirtool.main(['ncmirtool.py', 'cilupload', 'foo'])
        self.assertTrue(res > 0)


if __name__ == '__main__':  # pragma: no cover
    sys.exit(unittest.main())
