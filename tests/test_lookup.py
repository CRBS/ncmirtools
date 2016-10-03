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
import re
import unittest

from ncmirtools.lookup import DirectoryForMicroscopyProductId
from ncmirtools.lookup import DirectorySearchPathError
from ncmirtools.lookup import InvalidMicroscopyProductIdError


class TestLookup(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_DirectoryForMicroscopyProductId_constructor(self):

        # try passing none to constructor
        try:
            DirectoryForMicroscopyProductId(None)
            self.fail('Expected DirectorySearchPathError')
        except DirectorySearchPathError as e:
            self.assertEqual(str(e),
                             'search_path passed into constructor '
                             'cannot be None')

        # try passing invalid search_path
        bad_path = '/c/<VOLUME_ID>/<PROJECT_ID>/hi'
        try:

            DirectoryForMicroscopyProductId(bad_path)
            self.fail('Expected DirectorySearchPathError')
        except DirectorySearchPathError as e:
            self.assertEqual(str(e),
                             'Invalid search_path passed into '
                             'constructor : ' + bad_path)

        # try valid path
        DirectoryForMicroscopyProductId(
            DirectoryForMicroscopyProductId.PROJECT_DIR)

    def test__get_matching_directories(self):
        temp_dir = tempfile.mkdtemp()
        try:
            # try Passing None as arguments
            dmp = DirectoryForMicroscopyProductId(
                DirectoryForMicroscopyProductId.PROJECT_DIR)
            self.assertEqual(len(dmp._get_matching_directories(None, None)),
                             0)
            self.assertEqual(len(dmp._get_matching_directories(temp_dir,
                                                               None)),
                             0)

            # try on empty dir with exact match on and off
            res = dmp._get_matching_directories(temp_dir, 'foo')
            self.assertEqual(len(res), 0)

            res = dmp._get_matching_directories(temp_dir, 'foo',
                                                exactmatch=True)
            self.assertEqual(len(res), 0)

            foodir = os.path.join(temp_dir, 'microscopy_12345')
            os.makedirs(foodir)

            # try with file as prefix
            afile = os.path.join(temp_dir, 'somefile')
            open(afile, 'a').close()
            res = dmp._get_matching_directories(temp_dir, 'somefile')
            self.assertEqual(len(res), 0)

            res = dmp._get_matching_directories(temp_dir, 'somefile',
                                                exactmatch=True)
            self.assertEqual(len(res), 0)

            # try with one non exact match
            res = dmp._get_matching_directories(temp_dir, 'microscopy_')
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0], foodir)

            # try with exactmatch set to None
            res = dmp._get_matching_directories(temp_dir, 'microscopy_',
                                                exactmatch=None)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0], foodir)

            # try with exactmatch set to True but not an actual match
            res = dmp._get_matching_directories(temp_dir, 'microscopy_',
                                                exactmatch=True)
            self.assertEqual(len(res), 0)

            # try with exact match set to True and is an exact match
            res = dmp._get_matching_directories(temp_dir, 'microscopy_12345',
                                                exactmatch=True)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0], foodir)

            # try with exact match set to False and is an exact match
            res = dmp._get_matching_directories(temp_dir, 'microscopy_12345',
                                                exactmatch=False)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0], foodir)

            # try with multiple matching directories
            footwodir = os.path.join(temp_dir, 'microscopy_66')
            os.makedirs(footwodir)
            nonmatchdir = os.path.join(temp_dir, 'icroscopy_')
            os.makedirs(nonmatchdir)

            res = dmp._get_matching_directories(temp_dir, 'microscopy_',)
            self.assertEqual(len(res), 2)
            self.assertTrue(foodir in res)
            self.assertTrue(footwodir in res)

            res = dmp._get_matching_directories(temp_dir, 'microscopy_66',
                                                exactmatch=True)
            self.assertEqual(len(res), 1)
            self.assertTrue(footwodir in res)
        finally:
            shutil.rmtree(temp_dir)

    def test_get_directory_for_microscopy_product_id(self):
        temp_dir = tempfile.mkdtemp()
        try:
            # TODO: Make re.sub platform agnostic
            pdir = re.sub('^/', '',
                          DirectoryForMicroscopyProductId.PROJECT_DIR)

            sp = os.path.join(temp_dir, pdir)
            dmp = DirectoryForMicroscopyProductId(sp)

            # test mpid is None
            try:
                dmp.get_directory_for_microscopy_product_id(None)
                self.fail('Expected InvalidMicroscopyProductIdError')
            except InvalidMicroscopyProductIdError as e:
                self.assertEqual(str(e), 'microscopy product id cannot be '
                                         'None')

            # try on empty dir
            res = dmp.get_directory_for_microscopy_product_id(12345)
            self.assertEqual(len(res), 0)

            # TODO: Make path platform agnostic
            # try with 1 volume and no project
            volone = os.path.join(temp_dir, 'ccdbprod/ccdbprod1')
            os.makedirs(volone)
            res = dmp.get_directory_for_microscopy_product_id(12345)
            self.assertEqual(len(res), 0)

            # TODO: Make path platform agnostic
            # try with 1 volume, 1 project
            projone = os.path.join(volone, 'home/CCDB_DATA_USER.portal/'
                                           'CCDB_DATA_USER/acquisition/'
                                           'project_200000')
            os.makedirs(projone)
            res = dmp.get_directory_for_microscopy_product_id(12345)
            self.assertEqual(len(res), 0)

            # try with 1 volume 1 project, 1 microscopy id
            mpidone = os.path.join(projone, 'microscopy_12345')
            os.makedirs(mpidone)
            res = dmp.get_directory_for_microscopy_product_id(12345)
            self.assertEqual(len(res), 1)
            self.assertTrue(mpidone in res)

            # TODO: Make path platform agnostic
            # try with multiple volumes, projects & microscopy ids
            for val in range(2, 20, 1):
                avol = os.path.join(temp_dir, 'ccdbprod/ccdbprod' + str(val))
                os.makedirs(avol)
                for prj in range(300000, 300005, 1):
                    aprj = os.path.join(avol,
                                        'home/CCDB_DATA_USER.portal/'
                                        'CCDB_DATA_USER/acquisition/'
                                        'project_' + str(prj))
                    os.makedirs(aprj)
                    for mp in range(1, 5, 1):
                        ampid = os.path.join(aprj, 'microscopy_' + str(mp))
                        os.makedirs(ampid)
            res = dmp.get_directory_for_microscopy_product_id(12345)
            self.assertEqual(len(res), 1)
            self.assertTrue(mpidone in res)

            res = dmp.get_directory_for_microscopy_product_id(4)
            self.assertEqual(len(res), 90)

        finally:
            shutil.rmtree(temp_dir)

if __name__ == '__main__':
    sys.exit(unittest.main())
