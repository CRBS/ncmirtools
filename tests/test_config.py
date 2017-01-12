#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_lookup
----------------------------------

Tests for `lookup` module.
"""
import shutil
import tempfile
import sys
import unittest
import os
import configparser
import logging

from ncmirtools.config import ConfigMissingError
from ncmirtools.config import NcmirToolsConfig
from ncmirtools import config


class TestConfig(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_setup_logging(self):

        logger = logging.getLogger('fooey')

        config.setup_logging(logger)
        self.assertEqual(logging.getLogger
                         ('ncmirtools.projectsearch').getEffectiveLevel(),
                         logging.WARNING)

        config.setup_logging(logger, loglevel='DEBUG')
        self.assertEqual(logger.getEffectiveLevel(),
                         logging.DEBUG)
        self.assertEqual(logging.getLogger
                         ('ncmirtools.projectsearch').getEffectiveLevel(),
                         logging.DEBUG)
        self.assertEqual(logging.getLogger
                         ('ncmirtools.lookup').getEffectiveLevel(),
                         logging.DEBUG)
        self.assertEqual(logging.getLogger
                         ('ncmirtools.projectdir').getEffectiveLevel(),
                         logging.DEBUG)
        self.assertEqual(logging.getLogger
                         ('ncmirtools.lookup').getEffectiveLevel(),
                         logging.DEBUG)

        config.setup_logging(logger, loglevel='INFO')
        self.assertEqual(logging.getLogger
                         ('ncmirtools.projectdir').getEffectiveLevel(),
                         logging.INFO)

        config.setup_logging(logger, loglevel='ERROR')
        self.assertEqual(logging.getLogger
                         ('ncmirtools.projectdir').getEffectiveLevel(),
                         logging.ERROR)

        config.setup_logging(logger, loglevel='CRITICAL')
        self.assertEqual(logging.getLogger
                         ('ncmirtools.projectdir').getEffectiveLevel(),
                         logging.CRITICAL)

    def test_home_directory(self):
        con = NcmirToolsConfig()

        path = os.path.expanduser('~')
        self.assertEqual(con.get_home_directory(), path)

        con.set_home_directory('/foo')
        self.assertEqual(con.get_home_directory(), '/foo')

    def test_etc_directory(self):
        con = NcmirToolsConfig()
        self.assertEqual(con.get_etc_directory(), NcmirToolsConfig.ETC_DIR)
        con.set_etc_directory('/foo')
        self.assertEqual(con.get_etc_directory(), '/foo')

    def test_get_config_file(self):
        con = NcmirToolsConfig()

        path = os.path.expanduser('~')
        self.assertEqual(con.get_home_directory(), path)
        self.assertEqual(con.get_config_files(),
                         [os.path.join(NcmirToolsConfig.ETC_DIR,
                                       NcmirToolsConfig.CONFIG_FILE),
                          os.path.join(path,
                                       NcmirToolsConfig.UCONFIG_FILE)])

    def test_get_config_no_config_file_exists(self):
        temp_dir = tempfile.mkdtemp()
        try:
            con = NcmirToolsConfig()
            con.set_home_directory(temp_dir)
            con.set_etc_directory(os.path.join(temp_dir, 'etc'))
            try:
                con.get_config()
                self.fail('Expected ConfigMissingError')
            except ConfigMissingError as e:
                self.assertEqual(str(e),
                                 'No configuration file found in paths: ' +
                                 ', '.join(con.get_config_files()))
        finally:
            shutil.rmtree(temp_dir)

    def test_get_config_valid_config(self):
        temp_dir = tempfile.mkdtemp()
        try:
            con = NcmirToolsConfig()
            con.set_home_directory(temp_dir)

            initialcon = configparser.ConfigParser()
            initialcon.add_section(NcmirToolsConfig.POSTGRES_SECTION)
            initialcon.set(NcmirToolsConfig.POSTGRES_SECTION,
                           NcmirToolsConfig.POSTGRES_USER,
                           'bob')
            f = open(con.get_config_files()[1], 'w')
            initialcon.write(f)
            f.flush()
            f.close()
            con = NcmirToolsConfig()
            con.set_home_directory(temp_dir)
            config = con.get_config()

            val = config.get(NcmirToolsConfig.POSTGRES_SECTION,
                             NcmirToolsConfig.POSTGRES_USER)

            self.assertEqual(val, 'bob')
        finally:
            shutil.rmtree(temp_dir)

if __name__ == '__main__':
    sys.exit(unittest.main())
