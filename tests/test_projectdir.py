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

from ncmirtools import projectdir
from ncmirtools.lookup import DirectoryForId


class TestProjectdir(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_setup_logging(self):
        params = projectdir.Parameters()
        params.loglevel = 'DEBUG'
        projectdir._setup_logging(params)
        self.assertEqual(params.numericloglevel, logging.DEBUG)
        self.assertEqual(logging.getLogger
                         ('ncmirtools.projectdir').getEffectiveLevel(),
                         logging.DEBUG)
        self.assertEqual(logging.getLogger
                         ('ncmirtools.lookup').getEffectiveLevel(),
                         logging.DEBUG)

        params.loglevel = 'WARNING'
        projectdir._setup_logging(params)
        self.assertEqual(params.numericloglevel, logging.WARNING)
        self.assertEqual(logging.getLogger
                         ('ncmirtools.projectdir').getEffectiveLevel(),
                         logging.WARNING)
        self.assertEqual(logging.getLogger
                         ('ncmirtools.lookup').getEffectiveLevel(),
                         logging.WARNING)

        params.loglevel = 'INFO'
        projectdir._setup_logging(params)
        self.assertEqual(params.numericloglevel, logging.INFO)

        params.loglevel = 'ERROR'
        projectdir._setup_logging(params)
        self.assertEqual(params.numericloglevel, logging.ERROR)

        params.loglevel = 'CRITICAL'
        projectdir._setup_logging(params)
        self.assertEqual(params.numericloglevel, logging.CRITICAL)

    def test_parse_arguments(self):
        pargs = projectdir._parse_arguments('hello', ['12345'])
        self.assertEqual(pargs.projectid, '12345')
        self.assertEqual(pargs.loglevel, 'WARNING')
        self.assertTrue(pargs.prefixdir.startswith(os.sep + 'ccdbprod'))

        pargs = projectdir._parse_arguments('hello', ['1xx', '--log',
                                                  'DEBUG', '--prefixdir',
                                                  'hi'])
        self.assertEqual(pargs.projectid, '1xx')
        self.assertEqual(pargs.loglevel, 'DEBUG')
        self.assertEqual(pargs.prefixdir, 'hi')

    def test_run_lookup(self):

        # simple test where we raise an exception
        self.assertEqual(projectdir._run_lookup(None, None), 2)

        # test with non matching mpid
        self.assertEqual(projectdir._run_lookup(
            DirectoryForId.PROJECT_DIR, 'doesnotexistxx'), 1)

        # test with a match
        temp_dir = tempfile.mkdtemp()
        try:
            pdir = re.sub('^/', '',
                          DirectoryForId.PROJECT_DIR)
            mpdir = os.path.join(temp_dir, 'ccdbprod', 'ccdbprod1',
                                 'home', 'CCDB_DATA_USER.portal',
                                 'CCDB_DATA_USER', 'acquisition',
                                 'project_12345', 'microscopy_222')
            os.makedirs(mpdir)
            self.assertEqual(projectdir._run_lookup(os.path.join(temp_dir, pdir),
                                                '12345'), 0)
        finally:
            shutil.rmtree(temp_dir)

    def test_main(self):
        self.assertEqual(projectdir.main(), 1)


if __name__ == '__main__':
    sys.exit(unittest.main())
