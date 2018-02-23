#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_datafinder
----------------------------------

Tests for `datafinder` module.
"""

import shutil
import tempfile
import sys
import unittest
import os
import configparser

from ncmirtools.config import NcmirToolsConfig
from ncmirtools.kiosk import datafinder
from ncmirtools.kiosk.datafinder import FileFinder
from ncmirtools.kiosk.datafinder import SecondYoungestFromConfigFactory
from ncmirtools.kiosk.datafinder import SecondYoungest


class TestDataFinder(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_files_in_directory_generator_none_passed_in(self):

        count = 0
        for item in datafinder._get_files_in_directory_generator(None, None):
            count += 1
        self.assertEqual(count, 0)

    def test_get_files_in_directory_generator_on_empty_dir(self):
        temp_dir = tempfile.mkdtemp()
        try:

            count = 0
            for item in datafinder._get_files_in_directory_generator(temp_dir,
                                                                     None):
                count += 1
            self.assertEqual(count, 0)
        finally:
            shutil.rmtree(temp_dir)

    def test_get_files_in_directory_generator_on_one_file(self):
        temp_dir = tempfile.mkdtemp()
        try:
            count = 0
            onefile = os.path.join(temp_dir, 'foo.txt')
            open(onefile, 'a').close()

            for item in datafinder._get_files_in_directory_generator(onefile,
                                                                     None):
                self.assertEqual(item, onefile)
                count += 1

            self.assertEqual(count, 1)
        finally:
            shutil.rmtree(temp_dir)

    def test_get_files_in_directory_generator_on_dir_with_file(self):
        temp_dir = tempfile.mkdtemp()
        try:
            count = 0
            onefile = os.path.join(temp_dir, 'foo.txt')
            open(onefile, 'a').close()

            for item in datafinder._get_files_in_directory_generator(temp_dir,
                                                                     None):
                self.assertEqual(item, onefile)
                count += 1

            self.assertEqual(count, 1)
        finally:
            shutil.rmtree(temp_dir)

    def test_get_files_in_directory_generator_on_multiple_files(self):
        temp_dir = tempfile.mkdtemp()
        try:
            one = os.path.join(temp_dir, '1.txt')
            two = os.path.join(temp_dir, '2.txt')
            three = os.path.join(temp_dir, '3.txt')
            open(one, 'a').close()
            open(two, 'a').close()
            open(three, 'a').close()
            thefiles = []
            for item in datafinder._get_files_in_directory_generator(temp_dir,
                                                                     []):
                thefiles.append(item)
            self.assertTrue(one in thefiles)
            self.assertTrue(two in thefiles)
            self.assertTrue(three in thefiles)
            self.assertEqual(len(thefiles), 3)
        finally:
            shutil.rmtree(temp_dir)

    def test_get_files_in_directory_generator_on_multiple_directories(self):
        temp_dir = tempfile.mkdtemp()
        try:
            one = os.path.join(temp_dir, '1.txt')
            two = os.path.join(temp_dir, '2.txt')
            subdir = os.path.join(temp_dir, 'foodir')
            os.makedirs(subdir, mode=0o0775)
            three = os.path.join(subdir, '3.txt')
            four = os.path.join(subdir, '4.txt')
            open(one, 'a').close()
            open(two, 'a').close()
            open(three, 'a').close()
            open(four, 'a').close()
            thefiles = []
            for item in datafinder._get_files_in_directory_generator(temp_dir,
                                                                     None):
                thefiles.append(item)
            self.assertTrue(one in thefiles)
            self.assertTrue(two in thefiles)
            self.assertTrue(three in thefiles)
            self.assertTrue(four in thefiles)
            self.assertEqual(len(thefiles), 4)
        finally:
            shutil.rmtree(temp_dir)

    def test_get_files_in_directory_generator_with_exclude(self):
        temp_dir = tempfile.mkdtemp()
        try:
            one = os.path.join(temp_dir, '1.txt')
            two = os.path.join(temp_dir, '2.txt')
            subdir = os.path.join(temp_dir, 'foodir')
            os.makedirs(subdir, mode=0o0775)
            three = os.path.join(subdir, '3.txt')
            four = os.path.join(subdir, '4.txt')
            open(one, 'a').close()
            open(two, 'a').close()
            open(three, 'a').close()
            open(four, 'a').close()
            thefiles = []
            for item in datafinder._get_files_in_directory_generator(temp_dir,
                                                                     ['foodir',
                                                                      'blah']):
                thefiles.append(item)
            self.assertTrue(one in thefiles)
            self.assertTrue(two in thefiles)
            self.assertFalse(three in thefiles)
            self.assertFalse(four in thefiles)
            self.assertEqual(len(thefiles), 2)
        finally:
            shutil.rmtree(temp_dir)

    def test_filefinder(self):
        ff = FileFinder()
        try:
            ff.get_next_file()
            self.fail('Expected NotImplementedError')
        except NotImplementedError:
            pass

    def test_secondyoungestfromconfigfactory(self):
        # test with no config
        fac = SecondYoungestFromConfigFactory(None)
        filefinder, errmsg = fac.get_file_finder()
        self.assertEqual(filefinder, None)
        self.assertEqual(errmsg, 'No configuration passed into '
                                 'SecondYoungestFromConfigFactory')

        # test with empty config
        con = configparser.ConfigParser()
        fac = SecondYoungestFromConfigFactory(con)
        filefinder, errmsg = fac.get_file_finder()
        self.assertEqual(filefinder, None)
        self.assertEqual(errmsg, 'No [dataserver] section found in '
                                 'configuration. ')

        # test with missing section
        con.add_section(NcmirToolsConfig.DATASERVER_SECTION)
        fac = SecondYoungestFromConfigFactory(con)
        filefinder, errmsg = fac.get_file_finder()
        self.assertEqual(filefinder, None)
        self.assertEqual(errmsg, 'No datadir option found in '
                                 'configuration. ')

        # test with datadir set
        con.set(NcmirToolsConfig.DATASERVER_SECTION,
                NcmirToolsConfig.DATASERVER_DATADIR, '/foo')
        fac = SecondYoungestFromConfigFactory(con)
        filefinder, errmsg = fac.get_file_finder()
        self.assertEqual(filefinder.get_searchdir(), '/foo')
        self.assertEqual(filefinder.get_suffix(), None)
        self.assertEqual(filefinder.get_list_of_directories_to_exclude(), None)
        self.assertEqual(errmsg, None)

        # test with img suffix set
        con.set(NcmirToolsConfig.DATASERVER_SECTION,
                NcmirToolsConfig.DATASERVER_IMGSUFFIX, '.dm4')
        fac = SecondYoungestFromConfigFactory(con)
        filefinder, errmsg = fac.get_file_finder()
        self.assertEqual(filefinder.get_searchdir(), '/foo')
        self.assertEqual(filefinder.get_suffix(), '.dm4')
        self.assertEqual(filefinder.get_list_of_directories_to_exclude(), None)
        self.assertEqual(errmsg, None)

        # test with dirs to exclude set
        con.set(NcmirToolsConfig.DATASERVER_SECTION,
                NcmirToolsConfig.DATASERVER_DIRSTOEXCLUDE, 'blah')
        fac = SecondYoungestFromConfigFactory(con)
        filefinder, errmsg = fac.get_file_finder()
        self.assertEqual(filefinder.get_searchdir(), '/foo')
        self.assertEqual(filefinder.get_suffix(), '.dm4')
        self.assertEqual(filefinder.get_list_of_directories_to_exclude(),
                         ['blah'])
        self.assertEqual(errmsg, None)

        # test with dirs to exclude set to comma delimited list
        con.set(NcmirToolsConfig.DATASERVER_SECTION,
                NcmirToolsConfig.DATASERVER_DIRSTOEXCLUDE, 'blah,yo,hi')
        fac = SecondYoungestFromConfigFactory(con)
        filefinder, errmsg = fac.get_file_finder()
        self.assertEqual(filefinder.get_searchdir(), '/foo')
        self.assertEqual(filefinder.get_suffix(), '.dm4')
        self.assertEqual(filefinder.get_list_of_directories_to_exclude(),
                         ['blah', 'yo', 'hi'])
        self.assertEqual(errmsg, None)

    def test_get_second_youngest_image_file_searchdir_is_none(self):
        filefinder = SecondYoungest(None, None, None)
        res = filefinder.get_next_file()
        self.assertEqual(res, None)

    def test_get_second_youngest_image_file_searchdir_nofiles(self):
        temp_dir = tempfile.mkdtemp()
        try:
            filefinder = SecondYoungest(temp_dir, None, ['foo'])
            res = filefinder.get_next_file()
            self.assertEqual(res, None)
        finally:
            shutil.rmtree(temp_dir)

    def test_second_youngest_image_file_searchdir_onefile(self):
        temp_dir = tempfile.mkdtemp()
        try:

            onefile = os.path.join(temp_dir, 'foo.dm4')
            open(onefile, 'a').close()
            filefinder = SecondYoungest(temp_dir, '.dm4', ['foo'])
            res = filefinder.get_next_file()
            self.assertEqual(res, None)
        finally:
            shutil.rmtree(temp_dir)

    def test_second_youngest_image_file_searchdir_twofiles(self):
        temp_dir = tempfile.mkdtemp()
        try:
            onefile = os.path.join(temp_dir, 'foo.dm4')
            open(onefile, 'a').close()
            os.utime(onefile, (100, 100))
            twofile = os.path.join(temp_dir, 'foo2.dm4')
            open(twofile, 'a').close()
            os.utime(twofile, (20000, 20000))

            filefinder = SecondYoungest(temp_dir, '.dm4', ['foo'])
            res = filefinder.get_next_file()
            self.assertEqual(res, onefile)
        finally:
            shutil.rmtree(temp_dir)

    def test_second_youngest_image_file_searchdir_fourfilestwodirs(self):
        temp_dir = tempfile.mkdtemp()
        try:
            onefile = os.path.join(temp_dir, 'foo.dm4')
            open(onefile, 'a').close()
            os.utime(onefile, (500, 500))
            twofile = os.path.join(temp_dir, 'foo2.dm4')
            open(twofile, 'a').close()
            os.utime(twofile, (510, 510))

            subdir = os.path.join(temp_dir, 'anotherdir')
            os.makedirs(subdir, mode=0o0775)
            three = os.path.join(subdir, '3.dm4')
            open(three, 'a').close()
            os.utime(three, (700, 700))
            four = os.path.join(subdir, '4.dm4')
            open(four, 'a').close()
            os.utime(four, (701, 701))
            filefinder = SecondYoungest(temp_dir, '.dm4', ['foodir'])
            res = filefinder.get_next_file()
            self.assertEqual(res, three)
        finally:
            shutil.rmtree(temp_dir)

    def test_second_youngest_image_file_searchdir_suffix_test(self):
        temp_dir = tempfile.mkdtemp()
        try:
            onefile = os.path.join(temp_dir, 'foo.dm4')
            open(onefile, 'a').close()
            os.utime(onefile, (500, 500))
            twofile = os.path.join(temp_dir, 'foo2.dm4')
            open(twofile, 'a').close()
            os.utime(twofile, (510, 510))

            subdir = os.path.join(temp_dir, 'dir')
            os.makedirs(subdir, mode=0o0775)
            three = os.path.join(subdir, '3.dm5')
            open(three, 'a').close()
            os.utime(three, (700, 700))
            four = os.path.join(subdir, 'dm4.txt')
            open(four, 'a').close()
            os.utime(four, (701, 701))
            filefinder = SecondYoungest(temp_dir, '.dm4', ['foodir'])
            res = filefinder.get_next_file()
            self.assertEqual(res, onefile)
        finally:
            shutil.rmtree(temp_dir)

    def test_second_youngest_image_file_searchdir_exclude_dir_test(self):
        temp_dir = tempfile.mkdtemp()
        try:
            onefile = os.path.join(temp_dir, 'foo.dm4')
            open(onefile, 'a').close()
            os.utime(onefile, (500, 500))
            twofile = os.path.join(temp_dir, 'foo2.dm4')
            open(twofile, 'a').close()
            os.utime(twofile, (510, 510))

            subdir = os.path.join(temp_dir, 'foodir')
            os.makedirs(subdir, mode=0o0775)
            three = os.path.join(subdir, '3.dm4')
            open(three, 'a').close()
            os.utime(three, (700, 700))
            four = os.path.join(subdir, '4.dm4')
            open(four, 'a').close()
            os.utime(four, (701, 701))
            filefinder = SecondYoungest(temp_dir, '.dm4', ['foodir'])
            res = filefinder.get_next_file()
            self.assertEqual(res, onefile)
        finally:
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    sys.exit(unittest.main())
