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
import logging
import tempfile
import shutil
import unittest

from ncmirtools import projectsearch


class TestProjectdir(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_setup_logging(self):
        params = projectsearch.Parameters()
        params.loglevel = 'DEBUG'
        projectsearch._setup_logging(params)
        self.assertEqual(params.numericloglevel, logging.DEBUG)
        self.assertEqual(logging.getLogger
                         ('ncmirtools.projectsearch').getEffectiveLevel(),
                         logging.DEBUG)
        self.assertEqual(logging.getLogger
                         ('ncmirtools.lookup').getEffectiveLevel(),
                         logging.DEBUG)

        params.loglevel = 'WARNING'
        projectsearch._setup_logging(params)
        self.assertEqual(params.numericloglevel, logging.WARNING)
        self.assertEqual(logging.getLogger
                         ('ncmirtools.projectsearch').getEffectiveLevel(),
                         logging.WARNING)
        self.assertEqual(logging.getLogger
                         ('ncmirtools.lookup').getEffectiveLevel(),
                         logging.WARNING)

        params.loglevel = 'INFO'
        projectsearch._setup_logging(params)
        self.assertEqual(params.numericloglevel, logging.INFO)

        params.loglevel = 'ERROR'
        projectsearch._setup_logging(params)
        self.assertEqual(params.numericloglevel, logging.ERROR)

        params.loglevel = 'CRITICAL'
        projectsearch._setup_logging(params)
        self.assertEqual(params.numericloglevel, logging.CRITICAL)

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
        self.assertTrue(projectsearch.main() >= 0)


if __name__ == '__main__':
    sys.exit(unittest.main())
