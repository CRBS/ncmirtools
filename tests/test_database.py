#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_database
----------------------------------

Tests for `Database` class.
"""

import sys
import unittest
from mock import Mock
import configparser
from pg8000 import InterfaceError

from ncmirtools.lookup import Database
from ncmirtools.config import NcmirToolsConfig


class TestDatabase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_connection(self):
        config = configparser.ConfigParser()
        config.add_section(NcmirToolsConfig.POSTGRES_SECTION)
        config.set(NcmirToolsConfig.POSTGRES_SECTION,
                   NcmirToolsConfig.POSTGRES_USER, 'yo')
        config.set(NcmirToolsConfig.POSTGRES_SECTION,
                   NcmirToolsConfig.POSTGRES_PASS, 'yo')
        config.set(NcmirToolsConfig.POSTGRES_SECTION,
                   NcmirToolsConfig.POSTGRES_HOST, 'localhost')
        config.set(NcmirToolsConfig.POSTGRES_SECTION,
                   NcmirToolsConfig.POSTGRES_PORT, '5')
        config.set(NcmirToolsConfig.POSTGRES_SECTION,
                   NcmirToolsConfig.POSTGRES_DB, 'yo')

        db = Database(config)
        mockcon = Mock()
        db = Database(config)

        db.set_alternate_connection(mockcon)
        c = db.get_connection()
        self.assertEqual(c, mockcon)
        db.set_config(config)
        db.set_alternate_connection(None)
        try:
            c = db.get_connection()
            self.fail('Expected InterfaceError, course this requires'
                      'postgres NOT to be running on localhost listening'
                      'on port 5')
        except InterfaceError as e:
            self.assertTrue(str(e).startswith("('communication error'"))


if __name__ == '__main__':
    sys.exit(unittest.main())
