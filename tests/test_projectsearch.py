#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_lookup
----------------------------------

Tests for `lookup` module.
"""

import sys
import unittest

from ncmirtools import projectsearch


class TestProjectdir(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_arguments(self):
        pargs = projectsearch._parse_arguments('hello', ['12345'])
        self.assertEqual(pargs.keyword, '12345')
        self.assertEqual(pargs.loglevel, 'WARNING')
        self.assertEqual(pargs.homedir, '~')

        pargs = projectsearch._parse_arguments('hello', ['1xx', '--log',
                                                         'DEBUG', '--homedir',
                                                         'foo'])
        self.assertEqual(pargs.keyword, '1xx')
        self.assertEqual(pargs.loglevel, 'DEBUG')
        self.assertEqual(pargs.homedir, 'foo')

    def test_main(self):
        self.assertTrue(projectsearch.main(['projectsearch.py',
                                            'somearg']) >= 0)


if __name__ == '__main__':
    sys.exit(unittest.main())
