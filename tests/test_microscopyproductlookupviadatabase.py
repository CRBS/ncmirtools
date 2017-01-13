#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_microscopyproductlookupviadatabase
----------------------------------

Tests for `MicroscopyProuctLookupViaDatabase` class.
"""

import sys
import unittest
from mock import Mock
import math
import configparser

from ncmirtools.lookup import MicroscopyProductLookupViaDatabase


class TestMicroscopyProductLookupViaDatabase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_microscopyproduct_for_id_invalid_id_passed_in(self):
        ps = MicroscopyProductLookupViaDatabase(configparser.ConfigParser())

        # None
        res = ps.get_microscopyproduct_for_id(None)
        self.assertEqual(res, None)

        # string passed in
        res = ps.get_microscopyproduct_for_id('123')
        self.assertEqual(res, None)

        # float passed in
        res = ps.get_microscopyproduct_for_id(1.2)
        self.assertEqual(res, None)

        # to large of a value
        maxval = MicroscopyProductLookupViaDatabase.MAX_MPID
        res = ps.get_microscopyproduct_for_id(maxval)
        self.assertEqual(res, None)

    def test_get_microscopyproduct_for_id_no_matching_id(self):
        ps = MicroscopyProductLookupViaDatabase(configparser.ConfigParser())

        mockcon = Mock()
        mcursor = Mock()
        mcursor.rowcount = 0
        mcursor.fetchone = Mock(return_value=('basename', 'somenotes'))
        mockcon.cursor = Mock(return_value=mcursor)

        ps.set_alternate_connection(mockcon)
        res = ps.get_microscopyproduct_for_id(123)

        mcursor.execute.assert_called_with("SELECT image_basename,notes FROM "
                                           "Microscopy_products "
                                           "WHERE mpid='123'")
        mcursor.close.assert_called_once_with()
        mockcon.commit.assert_called_once_with()
        mockcon.close.assert_called_once_with()
        self.assertEqual(res, None)

    def test_get_microscopyproduct_for_id_rowcount_negative(self):
        ps = MicroscopyProductLookupViaDatabase(configparser.ConfigParser())
        ps.set_config(configparser.ConfigParser())
        mockcon = Mock()
        mcursor = Mock()
        mcursor.rowcount = -1
        mcursor.fetchone = Mock(return_value=('basename', 'somenotes'))
        mockcon.cursor = Mock(return_value=mcursor)

        ps.set_alternate_connection(mockcon)
        res = ps.get_microscopyproduct_for_id(123)

        mcursor.execute.assert_called_with("SELECT image_basename,notes FROM "
                                           "Microscopy_products "
                                           "WHERE mpid='123'")
        mcursor.close.assert_called_once_with()
        mockcon.commit.assert_called_once_with()
        mockcon.close.assert_called_once_with()
        self.assertEqual(res, None)

    def test_get_microscopyproduct_for_id_success(self):
        ps = MicroscopyProductLookupViaDatabase(configparser.ConfigParser())

        mockcon = Mock()
        mcursor = Mock()
        mcursor.rowcount = 2
        mcursor.fetchone = Mock(return_value=('basename', 'somenotes'))
        mockcon.cursor = Mock(return_value=mcursor)

        ps.set_alternate_connection(mockcon)
        res = ps.get_microscopyproduct_for_id(123)

        mcursor.execute.assert_called_with("SELECT image_basename,notes FROM "
                                           "Microscopy_products "
                                           "WHERE mpid='123'")
        mcursor.close.assert_called_once_with()
        mockcon.commit.assert_called_once_with()
        mockcon.close.assert_called_once_with()
        self.assertEqual(res.get_image_basename(), 'basename')
        self.assertEqual(res.get_notes(), 'somenotes')
        self.assertEqual(res.get_mpid(), '123')


if __name__ == '__main__':
    sys.exit(unittest.main())
