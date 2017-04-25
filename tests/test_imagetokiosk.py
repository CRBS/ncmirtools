#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_imagetokiosk
----------------------------------

Tests for `imagetokiosk` module.
"""
import re
import os
import sys
import tempfile
import shutil
import unittest
import configparser
from configparser import NoOptionError
from configparser import NoSectionError

from ncmirtools import imagetokiosk
from ncmirtools.config import NcmirToolsConfig


class TestImagetokiosk(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_arguments(self):
        pargs = imagetokiosk._parse_arguments('some description', ['run'])
        self.assertEqual(pargs.mode, 'run')
        self.assertEqual(pargs.loglevel, 'WARNING')
        self.assertEqual(pargs.homedir, '~')

        pargs = imagetokiosk._parse_arguments('some description',
                                              ['dryrun',
                                               imagetokiosk.HOMEDIR_ARG,
                                               'home', '--log', 'DEBUG'])

        self.assertEqual(pargs.mode, 'dryrun')
        self.assertEqual(pargs.loglevel, 'DEBUG')
        self.assertEqual(pargs.homedir, 'home')

    def test_get_lock(self):
        temp_dir = tempfile.mkdtemp()
        try:
            # try passing a directory
            try:
                imagetokiosk._get_lock(temp_dir)
            except OSError as e:
                self.assertTrue('Is a directory:' in str(e) or
                                'Operation not permitted' in str(e))

            # try a valid lock
            lfile = os.path.join(temp_dir, 'somelock')
            res = imagetokiosk._get_lock(lfile)
            self.assertEqual(os.getpid(), res.read_pid())

            # try lock again where same pid
            res = imagetokiosk._get_lock(lfile)
            self.assertEqual(os.getpid(), res.read_pid())

            # put another pid in lockfile that exists so
            # we get an exception
            f = open(lfile, 'w')
            f.write(str(os.getppid()) + '\n')
            f.flush()
            f.close()
            try:
                imagetokiosk._get_lock(lfile)
            except Exception as e:
                self.assertTrue('imagetokiosk.py with pid ' in str(e))

        finally:
            shutil.rmtree(temp_dir)

    def test_get_files_in_directory_generator_none_passed_in(self):

        count = 0
        for item in imagetokiosk._get_files_in_directory_generator(None, None):
            count += 1
        self.assertEqual(count, 0)

    def test_get_files_in_directory_generator_on_empty_dir(self):
        temp_dir = tempfile.mkdtemp()
        try:

            count = 0
            for item in imagetokiosk._get_files_in_directory_generator(temp_dir,
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

            for item in imagetokiosk._get_files_in_directory_generator(onefile,
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

            for item in imagetokiosk._get_files_in_directory_generator(temp_dir,
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
            for item in imagetokiosk._get_files_in_directory_generator(temp_dir,
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
            for item in imagetokiosk._get_files_in_directory_generator(temp_dir,
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
            for item in imagetokiosk._get_files_in_directory_generator(temp_dir,
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

    def test_get_second_youngest_image_file_searchdir_is_none(self):
        res = imagetokiosk._get_second_youngest_image_file(None, None, None)
        self.assertEqual(res, None)

    def test_get_second_youngest_image_file_searchdir_nofiles(self):
        temp_dir = tempfile.mkdtemp()
        try:
            res = imagetokiosk._get_second_youngest_image_file(temp_dir,
                                                               None, ['foo'])
            self.assertEqual(res, None)
        finally:
            shutil.rmtree(temp_dir)

    def test_second_youngest_image_file_searchdir_onefile(self):
        temp_dir = tempfile.mkdtemp()
        try:
            onefile = os.path.join(temp_dir, 'foo.dm4')
            open(onefile, 'a').close()
            res = imagetokiosk._get_second_youngest_image_file(temp_dir,
                                                               'dm4', ['foo'])
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
            os.utime(onefile, (200, 200))

            res = imagetokiosk._get_second_youngest_image_file(temp_dir,
                                                               '.dm4', ['foo'])
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

            res = imagetokiosk._get_second_youngest_image_file(temp_dir,
                                                               '.dm4',
                                                               ['foodir'])
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

            res = imagetokiosk._get_second_youngest_image_file(temp_dir,
                                                               '.dm4',
                                                               ['foodir'])
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

            res = imagetokiosk._get_second_youngest_image_file(temp_dir,
                                                               '.dm4',
                                                               ['foodir'])
            self.assertEqual(res, onefile)
        finally:
            shutil.rmtree(temp_dir)

    def test_get_last_transferred_file(self):
        temp_dir = tempfile.mkdtemp()
        try:
            res = imagetokiosk._get_last_transferred_file(None)
            self.assertEqual(res, None)

            # no section test
            con = configparser.ConfigParser()
            try:
                res = imagetokiosk._get_last_transferred_file(con)
                self.fail('Expected NoSectionError')
            except NoSectionError:
                pass

            # no option test
            con.add_section(NcmirToolsConfig.DATASERVER_SECTION)
            try:
                res = imagetokiosk._get_last_transferred_file(con)
                self.fail('Expected NoOptionError')
            except NoOptionError:
                pass

            # no log file
            lfile = os.path.join(temp_dir, 'logfile')
            con.set(NcmirToolsConfig.DATASERVER_SECTION,
                    NcmirToolsConfig.DATASERVER_TRANSFERLOG, lfile)
            res = imagetokiosk._get_last_transferred_file(con)
            self.assertEqual(res, None)

            imagetokiosk._update_last_transferred_file('hello', con)
            res = imagetokiosk._get_last_transferred_file(con)
            self.assertEqual(res, 'hello')

            imagetokiosk._update_last_transferred_file(None, con)
            res = imagetokiosk._get_last_transferred_file(con)
            self.assertEqual(res, '')

        finally:
            shutil.rmtree(temp_dir)

    def test_update_last_transferred_file(self):
        temp_dir = tempfile.mkdtemp()
        try:
            imagetokiosk._update_last_transferred_file(None, None)


            lfile = os.path.join(temp_dir, 'logfile')

            # no section test
            con = configparser.ConfigParser()
            try:
                res = imagetokiosk._update_last_transferred_file('hi', con)
                self.fail('Expected NoSectionError')
            except NoSectionError:
                pass

            # no option test
            con.add_section(NcmirToolsConfig.DATASERVER_SECTION)
            try:
                res = imagetokiosk._update_last_transferred_file('hi', con)
                self.fail('Expected NoOptionError')
            except NoOptionError:
                pass

            # try passing directory as file
            con.set(NcmirToolsConfig.DATASERVER_SECTION,
                    NcmirToolsConfig.DATASERVER_TRANSFERLOG, temp_dir)
            imagetokiosk._update_last_transferred_file('yo', con)

            # no log file
            con.set(NcmirToolsConfig.DATASERVER_SECTION,
                    NcmirToolsConfig.DATASERVER_TRANSFERLOG, lfile)
            imagetokiosk._update_last_transferred_file('hello', con)

            f = open(lfile, 'r')
            self.assertEqual(f.read(), 'hello\n')
            f.close()

            f = open(lfile, 'w')
            f.write('hello\n')
            f.flush()
            f.close()
            imagetokiosk._update_last_transferred_file('bye', con)

            f = open(lfile, 'r')
            self.assertEqual(f.read(), 'bye\n')
            f.close()

            # try writing none
            imagetokiosk._update_last_transferred_file(None, con)

            f = open(lfile, 'r')
            self.assertEqual(f.read(), '')
            f.close()

        finally:
            shutil.rmtree(temp_dir)

if __name__ == '__main__':
    sys.exit(unittest.main())
