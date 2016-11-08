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
                   NcmirToolsConfig.POSTGRES_HOST, 'localhost')
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
            self.fail('Expected InterfaceError, course this requires'
                      'postgres NOT to be running on localhost listening'
                      'on port 5')
        except InterfaceError as e:
            self.assertTrue(str(e).startswith("('communication error'"))

    def test_get_matching_projects_no_keyword(self):
        ps = ProjectSearchViaDatabase(configparser.ConfigParser())

        mockcon = Mock()
        mcursor = Mock()
        mcursor.fetchall = Mock(return_value=[(1, 'koo'), (3, 'yo')])
        mockcon.cursor = Mock(return_value=mcursor)

        ps.set_alternate_connection(mockcon)
        res = ps.get_matching_projects(None)

        mcursor.execute.assert_called_with("SELECT Project_id,project_name FROM Project")
        mcursor.close.assert_called_once_with()
        mockcon.commit.assert_called_once_with()
        mockcon.close.assert_called_once_with()
        self.assertEqual(res, ['1    koo', '3    yo'])

    def test_get_matching_projects_with_keyword(self):
        ps = ProjectSearchViaDatabase(configparser.ConfigParser())

        mockcon = Mock()
        mcursor = Mock()
        mcursor.fetchall = Mock(return_value=[(1, 'koo'), (3, 'yo'), ('4', 'val val')])
        mockcon.cursor = Mock(return_value=mcursor)

        ps.set_alternate_connection(mockcon)
        res = ps.get_matching_projects('ha ha')

        mcursor.execute.assert_called_with("SELECT Project_id,project_name FROM Project "
                               "WHERE project_name ILIKE '%%ha ha%%' OR "
                               " project_desc ILIKE '%%ha ha%%'")
        mcursor.close.assert_called_once_with()
        mockcon.commit.assert_called_once_with()
        mockcon.close.assert_called_once_with()
        self.assertEqual(res, ['1    koo', '3    yo', '4    val val'])


if __name__ == '__main__':
    sys.exit(unittest.main())
