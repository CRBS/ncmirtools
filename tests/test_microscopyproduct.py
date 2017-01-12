#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_microscopyproduct
----------------------------------

Tests for `MicroscopyProduct` class.
"""

import sys
import unittest

from ncmirtools.lookup import MicroscopyProduct


class TestMicroscopyProduct(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_constructor(self):
        mp = MicroscopyProduct()
        self.assertEqual(mp.get_mpid(), None)
        self.assertEqual(mp.get_image_basename(), None)
        self.assertEqual(mp.get_notes(), None)

        mp = MicroscopyProduct(mpid=4, image_basename='blah',
                               notes='some notes')
        self.assertEqual(mp.get_mpid(), 4)
        self.assertEqual(mp.get_image_basename(), 'blah')
        self.assertEqual(mp.get_notes(), 'some notes')

    def test_get_as_string(self):
        mp = MicroscopyProduct()
        self.assertEqual(mp.get_as_string(), '\nId: None\n\nImage '
                                             'Basename:\n\n   None'
                                             '\n\nNotes:\n\n   None\n\n')

        mp = MicroscopyProduct(mpid=4, image_basename='blah',
                               notes='some notes')

        self.assertEqual(mp.get_as_string(), '\nId: 4\n\nImage Basename:'
                                             '\n\n   blah\n\nNotes:\n\n   '
                                             'some notes\n\n')


if __name__ == '__main__':
    sys.exit(unittest.main())
