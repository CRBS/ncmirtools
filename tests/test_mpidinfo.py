#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_mpidinfo
----------------------------------

Tests for `mpidinfo` module.
"""

import sys
import unittest

from ncmirtools import mpidinfo


class TestMpidInfo(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_arguments(self):
        pargs = mpidinfo._parse_arguments('hello', ['12345'])
        self.assertEqual(pargs.mpid, 12345)
        self.assertEqual(pargs.loglevel, 'WARNING')
        self.assertEqual(pargs.homedir, '~')

        pargs = mpidinfo._parse_arguments('hello', ['1', '--log',
                                                    'DEBUG', '--homedir',
                                                    'foo'])
        self.assertEqual(pargs.mpid, 1)
        self.assertEqual(pargs.loglevel, 'DEBUG')
        self.assertEqual(pargs.homedir, 'foo')

    def test_main(self):
        self.assertTrue(mpidinfo.main(['mpidinfo.py',
                                       '123']) >= 0)


if __name__ == '__main__':
    sys.exit(unittest.main())
