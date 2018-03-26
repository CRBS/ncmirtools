#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_lookup
----------------------------------

Tests for `lookup` module.
"""
import re
import os
import sys
import tempfile
import shutil
import unittest
import argparse
import configparser

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

if __name__ == '__main__':
    sys.exit(unittest.main())
