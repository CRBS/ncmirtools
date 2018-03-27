#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_lookup
----------------------------------

Tests for `lookup` module.
"""
import os
import sys
import tempfile
import shutil
import unittest
import argparse
import configparser

from mock import Mock

from ncmirtools import ciluploader
from ncmirtools.config import NcmirToolsConfig
from ncmirtools.ciluploader import CILUploaderFromConfigFactory
from ncmirtools.ciluploader import CILUploader


class Parameters(object):
    """dummy"""
    pass

class TestCILUploader(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_arguments(self):

        help_formatter = argparse.RawDescriptionHelpFormatter
        parser = argparse.ArgumentParser(description='hi',
                                         formatter_class=help_formatter)
        subparsers = parser.add_subparsers(description='Command to run. ',
                                           dest='command')
        ciluploader.get_argument_parser(subparsers)

        pargs =  parser.parse_args(['cilupload', 'hi'])
        self.assertEqual(pargs.command, 'cilupload')
        self.assertEqual(pargs.data, 'hi')
        self.assertEqual(pargs.homedir, '~')

    def test_get_run_help_string(self):
        p = Parameters()
        p.program = 'hi'
        res = ciluploader._get_run_help_string(p)
        self.assertEqual(res, 'Please run hi -h for more information.')

    def test_get_and_verifyconfigparserconfig_no_config(self):
        temp_dir = tempfile.mkdtemp()
        try:
            ntc = NcmirToolsConfig()
            ntc.set_etc_directory(temp_dir)
            ntc.set_home_directory(temp_dir)
            p = Parameters()
            p.homedir = None
            c, err = ciluploader._get_and_verifyconfigparserconfig(p,
                                                                   altconfig=ntc)
            self.assertEqual(c, None)
            self.assertTrue('No configuration file' in err)

        finally:
            shutil.rmtree(temp_dir)

    def test_get_and_verifyconfigparserconfig_no_section(self):
        temp_dir = tempfile.mkdtemp()
        try:
            ntc = NcmirToolsConfig()
            ntc.set_etc_directory(temp_dir)
            ntc.set_home_directory(temp_dir)
            cfile = os.path.join(temp_dir, NcmirToolsConfig.UCONFIG_FILE)
            con = configparser.ConfigParser()
            con.set(configparser.DEFAULTSECT, 'hi', 'yo')
            with open(cfile, 'w') as f:
                con.write(f)
                f.flush()
            p = Parameters()

            p.homedir = None
            c, err = ciluploader.\
                _get_and_verifyconfigparserconfig(p,
                                                  altconfig=ntc)
            self.assertEqual(c, None)
            self.assertTrue('section found in' in err)
        finally:
            shutil.rmtree(temp_dir)

    def test_get_and_verifyconfigparserconfig_valid(self):
        temp_dir = tempfile.mkdtemp()
        try:
            ntc = NcmirToolsConfig()
            ntc.set_etc_directory(temp_dir)
            ntc.set_home_directory(temp_dir)
            cfile = os.path.join(temp_dir, NcmirToolsConfig.UCONFIG_FILE)
            con = configparser.ConfigParser()
            con.set(configparser.DEFAULTSECT, 'hi', 'yo')
            con.add_section(CILUploaderFromConfigFactory.CONFIG_SECTION)
            con.set(CILUploaderFromConfigFactory.CONFIG_SECTION,
                    'gg', 'yy')
            with open(cfile, 'w') as f:
                con.write(f)
                f.flush()
            p = Parameters()

            p.homedir = None
            c, err = ciluploader.\
                _get_and_verifyconfigparserconfig(p,
                                                  altconfig=ntc)
            self.assertEqual(err, None)
            self.assertTrue(c is not None)

            val = c.get(CILUploaderFromConfigFactory.CONFIG_SECTION,
                        'gg')
            self.assertEqual(val, 'yy')
        finally:
            shutil.rmtree(temp_dir)

    def test_ciluploader_upload_and_register_data_no_invalid_params(self):
        uploader = CILUploader(None)
        res = uploader.upload_and_register_data('/foo')
        self.assertEqual(res, 1)

        uploader = CILUploader(Parameters(),restuser='foo',
                               restpassword='pass')
        res = uploader.upload_and_register_data('/foo')
        self.assertEqual(res, 2)

        uploader = CILUploader(Parameters(), resturl='foo',
                               restpassword='pass')
        res = uploader.upload_and_register_data('/foo')
        self.assertEqual(res, 3)

        uploader = CILUploader(Parameters(), restuser='foo',
                               resturl='pass')
        res = uploader.upload_and_register_data('/foo')
        self.assertEqual(res, 4)

        uploader = CILUploader(Parameters(), restuser='foo',
                               resturl='ha',
                               restpassword='pass')
        res = uploader.upload_and_register_data(None)
        self.assertEqual(res, 5)

    def test_ciluploader_upload_and_register_data_no_transfer_error(self):
        mock_trans = Parameters()
        mock_trans.connect = Mock()
        mock_trans.transfer_file = Mock(return_value=('bad', 0, -1))
        mock_trans.disconnect = Mock()
        uploader = CILUploader(mock_trans,resturl='https://foo.com',
                               restuser='bob', restpassword='haha')
        res = uploader.upload_and_register_data('/foo')
        self.assertEqual(res, 6)

        mock_trans.connect.assert_called()
        mock_trans.disconnect.assert_called()
        mock_trans.transfer_file.assert_called_with('/foo')

    def test_ciluploader_upload_and_register_data_no_post_fails(self):
        mock_trans = Parameters()
        mock_trans.connect = Mock()
        mock_trans.transfer_file = Mock(return_value=(None, 10, 100))
        mock_trans.get_destination_directory = Mock(return_value='/dest')
        mock_trans.disconnect = Mock()

        mockresp = Parameters()
        mockresp.text = ''
        mockresp.json = Mock(return_value='{"success":true,"ID":13}')
        mockresp.status_code = 404
        mock_sess = Parameters()
        mock_sess.post = Mock(return_value=mockresp)

        uploader = CILUploader(mock_trans, resturl='https://foo.com',
                               restuser='bob', restpassword='haha')

        res = uploader.upload_and_register_data('/foo',
                                                session=mock_sess)
        self.assertEqual(res, 7)
        mock_trans.get_destination_directory.assert_called()

    def test_ciluploader_upload_and_register_data_success(self):
        mock_trans = Parameters()
        mock_trans.connect = Mock()
        mock_trans.transfer_file = Mock(return_value=(None, 10, 100))
        mock_trans.get_destination_directory = Mock(return_value='/dest')
        mock_trans.disconnect = Mock()

        mockresp = Parameters()
        mockresp.text = ''
        mockresp.json = Mock(return_value='{"success":true,"ID":13}')
        mockresp.status_code = 200
        mock_sess = Parameters()
        mock_sess.post = Mock(return_value=mockresp)

        uploader = CILUploader(mock_trans, resturl='https://foo.com',
                               restuser='bob', restpassword='haha')

        res = uploader.upload_and_register_data('/foo',
                                                session=mock_sess)
        self.assertEqual(res, 0)
        mock_trans.get_destination_directory.assert_called()

    def test_ciluploader_upload_and_register_data_self_make_session(self):
        mock_trans = Parameters()
        mock_trans.connect = Mock()
        mock_trans.transfer_file = Mock(return_value=(None, 10, 100))
        mock_trans.get_destination_directory = Mock(return_value='/dest')
        mock_trans.disconnect = Mock()

        uploader = CILUploader(mock_trans,
                               resturl='https://asdlfkjasdf.invalid',
                               restuser='bob', restpassword='haha')

        try:
            uploader.upload_and_register_data('/foo')
        except Exception:
            pass


if __name__ == '__main__':
    sys.exit(unittest.main())
