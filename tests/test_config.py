#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_lookup
----------------------------------

Tests for `lookup` module.
"""
import os
import shutil
import tempfile
import sys
import unittest
import os
import configparser

from ncmirtools.config import ConfigMissingError
from ncmirtools.config import NcmirToolsConfig


class TestConfig(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_home_directory(self):
        con = NcmirToolsConfig()

        path = os.path.expanduser('~')
        self.assertEqual(con.get_home_directory(), path)

        con.set_home_directory('/foo')
        self.assertEqual(con.get_home_directory(), '/foo')

    def test_get_config_file(self):
        con = NcmirToolsConfig()

        path = os.path.expanduser('~')
        self.assertEqual(con.get_home_directory(), path)
        self.assertEqual(con.get_config_file(),
                         os.path.join(path,
                                      NcmirToolsConfig.CONFIG_FILE))

    def test_get_config_no_config_file_exists(self):
        temp_dir = tempfile.mkdtemp()
        try:
            con = NcmirToolsConfig()
            con.set_home_directory(temp_dir)

            try:
                config = con.get_config()
                self.fail('Expected ConfigMissingError')
            except ConfigMissingError as e:
                self.assertEqual(str(e),
                                 'No configuration file found here: ' +
                                 os.path.join(temp_dir,
                                              con.get_config_file()))
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
            f = open(con.get_config_file(), 'w')
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
