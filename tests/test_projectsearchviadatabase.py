#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_projectsearchviadatabase
----------------------------------

Tests for `ProjectSearchViaDatabase` class.
"""
import os
import shutil
import tempfile
import sys
import re
import unittest
from mock import Mock
import configparser
from pg8000 import InterfaceError

from ncmirtools.lookup import ProjectSearchViaDatabase
from ncmirtools.config import NcmirToolsConfig



class TestProjectSearchViaDatabase(unittest.TestCase):

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
                   NcmirToolsConfig.POSTGRES_HOST, 'yo')
        config.set(NcmirToolsConfig.POSTGRES_SECTION,
                   NcmirToolsConfig.POSTGRES_PORT, '5')
        config.set(NcmirToolsConfig.POSTGRES_SECTION,
                   NcmirToolsConfig.POSTGRES_DB, 'yo')

        ps = ProjectSearchViaDatabase(config)
        mockcon = Mock()
        ps.set_alternate_connection(mockcon)
        c = ps._get_connection()
        self.assertEqual(c, mockcon)
        ps.set_config(config)
        ps.set_alternate_connection(None)
        try:
            c = ps._get_connection()
            self.fail('Expected InterfaceError')
        except InterfaceError:
            pass

    


if __name__ == '__main__':
    sys.exit(unittest.main())
