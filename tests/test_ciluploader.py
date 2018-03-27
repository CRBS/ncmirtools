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

    def test_ciluploaderfromconfigfactory_get_sftptransfer_from_config(self):
        temp_dir = tempfile.mkdtemp()
        try:
            con = configparser.ConfigParser()
            fac = CILUploaderFromConfigFactory(con)
            trans, err = fac._get_sftptransfer_from_config()
            self.assertEqual(trans, None)
            self.assertEqual(err, 'No [' +
                             CILUploaderFromConfigFactory.CONFIG_SECTION +
                             '] section found in configuration.')
            con.add_section(CILUploaderFromConfigFactory.CONFIG_SECTION)

            trans, err = fac._get_sftptransfer_from_config()
            self.assertEqual(trans, None)
            self.assertEqual(err, 'No ' +
                             CILUploaderFromConfigFactory.HOST +
                             ' option found in configuration.')
            con.set(CILUploaderFromConfigFactory.CONFIG_SECTION,
                    CILUploaderFromConfigFactory.HOST, 'thehost')

            trans, err = fac._get_sftptransfer_from_config()
            self.assertEqual(trans, None)
            self.assertEqual(err, 'No ' +
                             CILUploaderFromConfigFactory.DEST_DIR +
                             ' option found in configuration.')

            con.set(CILUploaderFromConfigFactory.CONFIG_SECTION,
                    CILUploaderFromConfigFactory.DEST_DIR, 'dest')

            trans, err = fac._get_sftptransfer_from_config()
            self.assertTrue(trans is not None)
            self.assertEqual(err, None)
            self.assertEqual(trans.get_host(), 'thehost')
            self.assertEqual(trans.get_destination_directory(), 'dest')

            con.set(CILUploaderFromConfigFactory.CONFIG_SECTION,
                    CILUploaderFromConfigFactory.USERNAME, 'theuser')

            con.set(CILUploaderFromConfigFactory.CONFIG_SECTION,
                    CILUploaderFromConfigFactory.PORT, '12345')

            con.set(CILUploaderFromConfigFactory.CONFIG_SECTION,
                    CILUploaderFromConfigFactory.CON_TIMEOUT, '100')

            con.set(CILUploaderFromConfigFactory.CONFIG_SECTION,
                    CILUploaderFromConfigFactory.PRIVATE_KEY_PASS,
                    'theprivatekeypass')

            trans, err = fac._get_sftptransfer_from_config()
            self.assertTrue(trans is not None)
            self.assertEqual(err, None)
            self.assertEqual(trans.get_host(), 'thehost')
            self.assertEqual(trans.get_destination_directory(), 'dest')
            self.assertEqual(trans.get_port(), 12345)
            self.assertEqual(trans.get_connect_timeout(), 100)
            self.assertEqual(trans.get_username(), 'theuser')
            self.assertEqual(trans.get_passphrase(), 'theprivatekeypass')

            con.set(CILUploaderFromConfigFactory.CONFIG_SECTION,
                    CILUploaderFromConfigFactory.PRIVATE_KEY,
                    os.path.join(temp_dir, 'foo'))
            try:
                fac._get_sftptransfer_from_config()
                self.fail('Expect SftpTransfer to fail cause private key'
                          'is invalid')
            except IOError:
                pass
        finally:
            shutil.rmtree(temp_dir)

    def test_ciluploaderfromconfigfactory_get_rest_info_from_config(self):
        temp_dir = tempfile.mkdtemp()
        try:
            con = configparser.ConfigParser()
            fac = CILUploaderFromConfigFactory(con)
            url, user, user_pass, err = fac._get_rest_info_from_config()
            self.assertEqual(url, None)
            self.assertEqual(user, None)
            self.assertEqual(user_pass, None)
            self.assertEqual(err, 'No [' +
                             CILUploaderFromConfigFactory.CONFIG_SECTION +
                             '] section found in configuration.')
            con.add_section(CILUploaderFromConfigFactory.CONFIG_SECTION)

            url, user, user_pass, err = fac._get_rest_info_from_config()
            self.assertEqual(url, None)
            self.assertEqual(user, None)
            self.assertEqual(user_pass, None)
            self.assertEqual(err, 'No ' +
                             CILUploaderFromConfigFactory.REST_URL +
                             ' option found in configuration.')

            con.set(CILUploaderFromConfigFactory.CONFIG_SECTION,
                    CILUploaderFromConfigFactory.REST_URL, 'https://foo')
            url, user, user_pass, err = fac._get_rest_info_from_config()
            self.assertEqual(url, None)
            self.assertEqual(user, None)
            self.assertEqual(user_pass, None)
            self.assertEqual(err, 'No ' +
                             CILUploaderFromConfigFactory.REST_USER +
                             ' option found in configuration.')

            con.set(CILUploaderFromConfigFactory.CONFIG_SECTION,
                    CILUploaderFromConfigFactory.REST_USER, 'someuser')
            url, user, user_pass, err = fac._get_rest_info_from_config()
            self.assertEqual(url, None)
            self.assertEqual(user, None)
            self.assertEqual(user_pass, None)
            self.assertEqual(err, 'No ' +
                             CILUploaderFromConfigFactory.REST_PASS +
                             ' option found in configuration.')

            con.set(CILUploaderFromConfigFactory.CONFIG_SECTION,
                    CILUploaderFromConfigFactory.REST_PASS, 'somepass')
            url, user, user_pass, err = fac._get_rest_info_from_config()
            self.assertEqual(url, 'https://foo')
            self.assertEqual(user, 'someuser')
            self.assertEqual(user_pass, 'somepass')
            self.assertEqual(err, None)
        finally:
            shutil.rmtree(temp_dir)

    def test_ciluploaderfromconfigfactory_get_ciluploader(self):
        temp_dir = tempfile.mkdtemp()
        try:
            fac = CILUploaderFromConfigFactory(None)
            res = fac.get_ciluploader()
            self.assertEqual(res, None)

            con = configparser.ConfigParser()
            fac = CILUploaderFromConfigFactory(con)
            res = fac.get_ciluploader()
            self.assertEqual(res, None)

            con.add_section(CILUploaderFromConfigFactory.CONFIG_SECTION)
            con.set(CILUploaderFromConfigFactory.CONFIG_SECTION,
                    CILUploaderFromConfigFactory.HOST, 'thehost')
            con.set(CILUploaderFromConfigFactory.CONFIG_SECTION,
                    CILUploaderFromConfigFactory.DEST_DIR, 'dest')

            fac = CILUploaderFromConfigFactory(con)
            res = fac.get_ciluploader()
            self.assertEqual(res, None)

            con.set(CILUploaderFromConfigFactory.CONFIG_SECTION,
                    CILUploaderFromConfigFactory.REST_URL, 'https://foo')
            con.set(CILUploaderFromConfigFactory.CONFIG_SECTION,
                    CILUploaderFromConfigFactory.REST_USER, 'someuser')
            con.set(CILUploaderFromConfigFactory.CONFIG_SECTION,
                    CILUploaderFromConfigFactory.REST_PASS, 'somepass')
            fac = CILUploaderFromConfigFactory(con)
            res = fac.get_ciluploader()
            self.assertTrue(isinstance(res, CILUploader))




        finally:
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    sys.exit(unittest.main())
