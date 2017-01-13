#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_projectsearchviadatabase
----------------------------------

Tests for `ProjectSearchViaDatabase` class.
"""

import sys
import unittest
from mock import Mock
import configparser

from ncmirtools.lookup import ProjectSearchViaDatabase


class TestProjectSearchViaDatabase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_matching_projects_no_keyword(self):
        ps = ProjectSearchViaDatabase(configparser.ConfigParser())

        mockcon = Mock()
        mcursor = Mock()
        mcursor.fetchall = Mock(return_value=[(1, 'koo'), (3, 'yo')])
        mockcon.cursor = Mock(return_value=mcursor)

        ps.set_alternate_connection(mockcon)
        res = ps.get_matching_projects(None)

        mcursor.execute.assert_called_with("SELECT Project_id,"
                                           "project_name FROM Project")
        mcursor.close.assert_called_once_with()
        mockcon.commit.assert_called_once_with()
        mockcon.close.assert_called_once_with()
        self.assertEqual(res, ['1    koo', '3    yo'])

    def test_get_matching_projects_with_keyword(self):
        ps = ProjectSearchViaDatabase(configparser.ConfigParser())

        mockcon = Mock()
        mcursor = Mock()
        mcursor.fetchall = Mock(return_value=[(1, 'koo'), (3, 'yo'),
                                              ('4', 'val val')])
        mockcon.cursor = Mock(return_value=mcursor)
        ps.set_config(configparser.ConfigParser())
        ps.set_alternate_connection(mockcon)

        res = ps.get_matching_projects('ha ha')

        mcursor.execute.assert_called_with("SELECT Project_id,project_name "
                                           "FROM Project "
                                           "WHERE project_name ILIKE "
                                           "'%%ha ha%%' OR "
                                           " project_desc ILIKE '%%ha ha%%'")
        mcursor.close.assert_called_once_with()
        mockcon.commit.assert_called_once_with()
        mockcon.close.assert_called_once_with()
        self.assertEqual(res, ['1    koo', '3    yo', '4    val val'])


if __name__ == '__main__':
    sys.exit(unittest.main())
