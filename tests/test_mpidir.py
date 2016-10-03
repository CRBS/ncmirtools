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

from ncmirtools import mpidir
from ncmirtools.lookup import DirectoryForMicroscopyProductId


class TestMpidir(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_setup_logging(self):
        params = mpidir.Parameters()
        params.loglevel = 'DEBUG'
        mpidir._setup_logging(params)
        self.assertEqual(params.numericloglevel, logging.DEBUG)
        self.assertEqual(logging.getLogger
                         ('ncmirtools.mpidir').getEffectiveLevel(),
                         logging.DEBUG)
        self.assertEqual(logging.getLogger
                         ('ncmirtools.lookup').getEffectiveLevel(),
                         logging.DEBUG)

        params.loglevel = 'WARNING'
        mpidir._setup_logging(params)
        self.assertEqual(params.numericloglevel, logging.WARNING)
        self.assertEqual(logging.getLogger
                         ('ncmirtools.mpidir').getEffectiveLevel(),
                         logging.WARNING)
        self.assertEqual(logging.getLogger
                         ('ncmirtools.lookup').getEffectiveLevel(),
                         logging.WARNING)

        params.loglevel = 'INFO'
        mpidir._setup_logging(params)
        self.assertEqual(params.numericloglevel, logging.INFO)

        params.loglevel = 'ERROR'
        mpidir._setup_logging(params)
        self.assertEqual(params.numericloglevel, logging.ERROR)

        params.loglevel = 'CRITICAL'
        mpidir._setup_logging(params)
        self.assertEqual(params.numericloglevel, logging.CRITICAL)

    def test_parse_arguments(self):
        pargs = mpidir._parse_arguments('hello', ['12345'])
        self.assertEqual(pargs.mpid, '12345')
        self.assertEqual(pargs.loglevel, 'WARNING')
        self.assertTrue(pargs.prefixdir.startswith(os.sep + 'ccdbprod'))

        pargs = mpidir._parse_arguments('hello', ['1xx', '--log',
                                                  'DEBUG', '--prefixdir',
                                                  'hi'])
        self.assertEqual(pargs.mpid, '1xx')
        self.assertEqual(pargs.loglevel, 'DEBUG')
        self.assertEqual(pargs.prefixdir, 'hi')

    def test_run_lookup(self):

        # simple test where we raise an exception
        self.assertEqual(mpidir._run_lookup(None, None), 2)

        # test with non matching mpid
        self.assertEqual(mpidir._run_lookup(
            DirectoryForMicroscopyProductId.PROJECT_DIR, 'doesnotexistxx'), 1)

        # test with a match
        temp_dir = tempfile.mkdtemp()
        try:
            pdir = re.sub('^/', '',
                          DirectoryForMicroscopyProductId.PROJECT_DIR)
            mpdir = os.path.join(temp_dir, 'ccdbprod', 'ccdbprod1',
                                 'home', 'CCDB_DATA_USER.portal',
                                 'CCDB_DATA_USER', 'acquisition',
                                 'project_2', 'microscopy_12345')
            os.makedirs(mpdir)
            self.assertEqual(mpidir._run_lookup(os.path.join(temp_dir, pdir),
                                                '12345'), 0)
        finally:
            shutil.rmtree(temp_dir)

    def test_main(self):
        self.assertEqual(mpidir.main(), 1)


if __name__ == '__main__':
    sys.exit(unittest.main())
