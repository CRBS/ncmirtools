#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_imagetokiosk
----------------------------------

Tests for `imagetokiosk` module.
"""
import os
import sys
import tempfile
import shutil
import unittest
import configparser
from configparser import NoOptionError
from configparser import NoSectionError
from mock import Mock


from ncmirtools import imagetokiosk
from ncmirtools.config import NcmirToolsConfig
from ncmirtools.kiosk.transfer import SftpTransfer


class TestImagetokiosk(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_arguments(self):
        pargs = imagetokiosk._parse_arguments('some description', ['run'])
        self.assertEqual(pargs.mode, 'run')
        self.assertEqual(pargs.loglevel, 'WARNING')

        pargs = imagetokiosk._parse_arguments('some description',
                                              ['dryrun',
                                               imagetokiosk.HOMEDIR_ARG,
                                               'home', '--log', 'DEBUG'])

        self.assertEqual(pargs.mode, 'dryrun')
        self.assertEqual(pargs.loglevel, 'DEBUG')
        self.assertEqual(pargs.homedir, 'home')

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
                imagetokiosk._update_last_transferred_file('hi', con)
                self.fail('Expected NoSectionError')
            except NoSectionError:
                pass

            # no option test
            con.add_section(NcmirToolsConfig.DATASERVER_SECTION)
            try:
                imagetokiosk._update_last_transferred_file('hi', con)
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

    def test_get_run_help_string(self):
        p = imagetokiosk.Parameters()
        p.program = 'foo'
        self.assertEqual(imagetokiosk._get_run_help_string(p),
                         'Please run foo -h for more information.')

    def test_get_and_verifyconfigparserconfig(self):
        p = imagetokiosk.Parameters()
        temp_dir = tempfile.mkdtemp()
        try:
            # test where no config
            p.homedir = temp_dir
            con, errmsg = imagetokiosk._get_and_verifyconfigparserconfig(p)
            self.assertEqual(con, None)
            self.assertTrue('No configuration file found ' in errmsg)

            # test with no dataserver section
            c = configparser.ConfigParser()
            c.set(configparser.DEFAULTSECT, 'hi', 'foo')
            cfile = os.path.join(temp_dir, NcmirToolsConfig.UCONFIG_FILE)
            f = open(cfile, 'w')
            c.write(f)
            f.flush()
            f.close()
            p.program = 'foo'
            con, errmsg = imagetokiosk._get_and_verifyconfigparserconfig(p)
            self.assertEqual(con, None)
            self.assertEqual(errmsg, 'No [dataserver] section found in '
                                     'configuration. Please run foo -h for '
                                     'more information.')

            # valid
            c.add_section(NcmirToolsConfig.DATASERVER_SECTION)
            f = open(cfile, 'w')
            c.write(f)
            f.flush()
            f.close()
            con, errmsg = imagetokiosk._get_and_verifyconfigparserconfig(p)
            self.assertTrue(con is not None)
            self.assertEqual(errmsg, None)
        finally:
            shutil.rmtree(temp_dir)

    def test_get_file_finder(self):
        # test with no config
        con = configparser.ConfigParser()
        p = imagetokiosk.Parameters()
        p.program = 'foo'
        filefinder, errmsg = imagetokiosk._get_file_finder(p, con)
        self.assertEqual(filefinder, None)
        self.assertTrue('found in configuration' in errmsg)

        # test valid config
        con.add_section(NcmirToolsConfig.DATASERVER_SECTION)
        con.set(NcmirToolsConfig.DATASERVER_SECTION,
                NcmirToolsConfig.DATASERVER_DATADIR, '/foo')
        filefinder, errmsg = imagetokiosk._get_file_finder(p, con)
        self.assertEqual(filefinder.get_searchdir(), '/foo')
        self.assertEqual(errmsg, None)

    def test_upload_image_file_get_sftptransfer(self):
        temp_dir = tempfile.mkdtemp()
        try:
            p = imagetokiosk.Parameters()
            p.mode = imagetokiosk.RUN_MODE
            p.program = 'foo'
            logfile = os.path.join(temp_dir, 'logfile.txt')
            con = configparser.ConfigParser()
            con.add_section(NcmirToolsConfig.DATASERVER_SECTION)
            con.set(NcmirToolsConfig.DATASERVER_SECTION,
                    NcmirToolsConfig.DATASERVER_TRANSFERLOG, logfile)

            fakefile = os.path.join(temp_dir, 'foo.txt')
            open(fakefile, 'a').close()
            res = imagetokiosk._upload_image_file(p, fakefile, con)
            self.assertEqual(res, 4)
        finally:
            shutil.rmtree(temp_dir)

    def test_upload_image_file_success(self):
        temp_dir = tempfile.mkdtemp()
        try:
            p = imagetokiosk.Parameters()
            p.mode = imagetokiosk.RUN_MODE
            logfile = os.path.join(temp_dir, 'logfile.txt')
            con = configparser.ConfigParser()
            con.add_section(NcmirToolsConfig.DATASERVER_SECTION)
            con.set(NcmirToolsConfig.DATASERVER_SECTION,
                    NcmirToolsConfig.DATASERVER_TRANSFERLOG, logfile)

            fakefile = os.path.join(temp_dir, 'foo.txt')
            open(fakefile, 'a').close()
            mt = SftpTransfer('foo.com', '/foo')
            mockssh = imagetokiosk.Parameters()
            mocksftp = imagetokiosk.Parameters()
            mockst = imagetokiosk.Parameters()
            mockst.st_size = 500
            mocksftp.put = Mock(return_value=mockst)
            mockssh.open_sftp = Mock(return_value=mocksftp)
            mt.set_alternate_connection(mockssh)
            res = imagetokiosk._upload_image_file(p, fakefile, con,
                                                  alt_transfer=mt)
            self.assertEqual(res, 0)
        finally:
            shutil.rmtree(temp_dir)

    def test_upload_image_file_success_dryrun(self):
        temp_dir = tempfile.mkdtemp()
        try:
            p = imagetokiosk.Parameters()
            p.mode = imagetokiosk.DRYRUN_MODE
            logfile = os.path.join(temp_dir, 'logfile.txt')
            con = configparser.ConfigParser()
            con.add_section(NcmirToolsConfig.DATASERVER_SECTION)
            con.set(NcmirToolsConfig.DATASERVER_SECTION,
                    NcmirToolsConfig.DATASERVER_TRANSFERLOG, logfile)

            fakefile = os.path.join(temp_dir, 'foo.txt')
            open(fakefile, 'a').close()
            mt = SftpTransfer('foo.com', '/foo')
            mockssh = imagetokiosk.Parameters()
            mocksftp = imagetokiosk.Parameters()
            mockst = imagetokiosk.Parameters()
            mockst.st_size = 500
            mocksftp.put = Mock(return_value=mockst)
            mockssh.open_sftp = Mock(return_value=mocksftp)
            mt.set_alternate_connection(mockssh)
            res = imagetokiosk._upload_image_file(p, fakefile, con,
                                                  alt_transfer=mt)
            self.assertEqual(res, 0)
        finally:
            shutil.rmtree(temp_dir)

    def test_upload_image_file_success_dryrun_alreadyuploaded(self):
        temp_dir = tempfile.mkdtemp()
        try:
            p = imagetokiosk.Parameters()
            p.mode = imagetokiosk.DRYRUN_MODE
            logfile = os.path.join(temp_dir, 'logfile.txt')
            con = configparser.ConfigParser()
            con.add_section(NcmirToolsConfig.DATASERVER_SECTION)
            con.set(NcmirToolsConfig.DATASERVER_SECTION,
                    NcmirToolsConfig.DATASERVER_TRANSFERLOG, logfile)

            fakefile = os.path.join(temp_dir, 'foo.txt')
            open(fakefile, 'a').close()
            imagetokiosk._update_last_transferred_file(fakefile, con)
            mt = SftpTransfer('foo.com', '/foo')
            mockssh = imagetokiosk.Parameters()
            mocksftp = imagetokiosk.Parameters()
            mockst = imagetokiosk.Parameters()
            mockst.st_size = 500
            mocksftp.put = Mock(return_value=mockst)
            mockssh.open_sftp = Mock(return_value=mocksftp)
            mt.set_alternate_connection(mockssh)
            res = imagetokiosk._upload_image_file(p, fakefile, con,
                                                  alt_transfer=mt)
            self.assertEqual(res, 0)
        finally:
            shutil.rmtree(temp_dir)

    def test_upload_image_file_fail(self):
        temp_dir = tempfile.mkdtemp()
        try:
            p = imagetokiosk.Parameters()
            p.mode = imagetokiosk.RUN_MODE
            logfile = os.path.join(temp_dir, 'logfile.txt')
            con = configparser.ConfigParser()
            con.add_section(NcmirToolsConfig.DATASERVER_SECTION)
            con.set(NcmirToolsConfig.DATASERVER_SECTION,
                    NcmirToolsConfig.DATASERVER_TRANSFERLOG, logfile)

            fakefile = os.path.join(temp_dir, 'foo.txt')
            open(fakefile, 'a').close()
            mt = SftpTransfer('foo.com', '/foo')
            mockssh = imagetokiosk.Parameters()
            mocksftp = imagetokiosk.Parameters()
            mockst = imagetokiosk.Parameters()
            mockst.st_size = 500
            mocksftp.put = Mock(side_effect=IOError('some error'))
            mockssh.open_sftp = Mock(return_value=mocksftp)
            mt.set_alternate_connection(mockssh)
            res = imagetokiosk._upload_image_file(p, fakefile, con,
                                                  alt_transfer=mt)
            self.assertEqual(res, 1)
        finally:
            shutil.rmtree(temp_dir)

    def test_check_and_transfer_image_invalid_config(self):
        temp_dir = tempfile.mkdtemp()
        try:
            con = configparser.ConfigParser()
            con.set(configparser.DEFAULTSECT, 'hi', 'someval')
            uconfig = os.path.join(temp_dir,
                                   NcmirToolsConfig.UCONFIG_FILE)
            f = open(uconfig, 'w')
            con.write(f)
            f.flush()
            f.close()
            p = imagetokiosk.Parameters()
            p.program = 'foo'
            p.homedir = temp_dir
            p.mode = imagetokiosk.RUN_MODE
            res = imagetokiosk._check_and_transfer_image(p)
            self.assertEqual(res, 2)
        finally:
            shutil.rmtree(temp_dir)

    def test_check_and_transfer_image_unable_to_load_filefinder(self):
        temp_dir = tempfile.mkdtemp()
        try:
            con = configparser.ConfigParser()
            con.add_section(NcmirToolsConfig.DATASERVER_SECTION)

            uconfig = os.path.join(temp_dir,
                                   NcmirToolsConfig.UCONFIG_FILE)
            f = open(uconfig, 'w')
            con.write(f)
            f.flush()
            f.close()
            p = imagetokiosk.Parameters()
            p.program = 'foo'
            p.homedir = temp_dir
            p.mode = imagetokiosk.RUN_MODE
            res = imagetokiosk._check_and_transfer_image(p)
            self.assertEqual(res, 3)
        finally:
            shutil.rmtree(temp_dir)

    def test_check_and_transfer_image_no_file_to_transfer(self):
        temp_dir = tempfile.mkdtemp()
        try:
            con = configparser.ConfigParser()
            con.add_section(NcmirToolsConfig.DATASERVER_SECTION)

            con.set(NcmirToolsConfig.DATASERVER_SECTION,
                    NcmirToolsConfig.DATASERVER_DATADIR, temp_dir)
            con.set(NcmirToolsConfig.DATASERVER_SECTION,
                    NcmirToolsConfig.DATASERVER_IMGSUFFIX, '.dm4')
            uconfig = os.path.join(temp_dir,
                                   NcmirToolsConfig.UCONFIG_FILE)
            f = open(uconfig, 'w')
            con.write(f)
            f.flush()
            f.close()
            p = imagetokiosk.Parameters()
            p.program = 'foo'
            p.homedir = temp_dir
            p.mode = imagetokiosk.DRYRUN_MODE
            res = imagetokiosk._check_and_transfer_image(p)
            self.assertEqual(res, 0)
        finally:
            shutil.rmtree(temp_dir)

    def test_main_no_file_to_transfer(self):
        temp_dir = tempfile.mkdtemp()
        try:
            con = configparser.ConfigParser()
            con.add_section(NcmirToolsConfig.DATASERVER_SECTION)

            con.set(NcmirToolsConfig.DATASERVER_SECTION,
                    NcmirToolsConfig.DATASERVER_DATADIR, temp_dir)
            con.set(NcmirToolsConfig.DATASERVER_SECTION,
                    NcmirToolsConfig.DATASERVER_IMGSUFFIX, '.dm4')
            uconfig = os.path.join(temp_dir,
                                   NcmirToolsConfig.UCONFIG_FILE)
            f = open(uconfig, 'w')
            con.write(f)
            f.flush()
            f.close()
            res = imagetokiosk.main(['foo', imagetokiosk.DRYRUN_MODE,
                                     imagetokiosk.HOMEDIR_ARG, temp_dir])

            self.assertEqual(res, 0)
        finally:
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    sys.exit(unittest.main())
