#! /usr/bin/env python

import os
import sys
import argparse
import ncmirtools
import logging

from ncmirtools.lookup import MicroscopyProductLookupViaDatabase
from ncmirtools.config import NcmirToolsConfig
from ncmirtools.config import ConfigMissingError
from ncmirtools import config


# create logger
logger = logging.getLogger(__name__)


def _get_argument_parser(subparsers):
    """Parses command line arguments using argparse.
    """
    desc = """
         This tool uploads data to Cell Image Library (CIL)
    
    
    """
    parser = subparsers.add_parser('cilupload',
                                   help='Uploads data to Cell Image '
                                        'Library (CIL)',
                                   description=desc)

    parser.add_argument("data", help='Data file to upload, can be an image or movie')
    parser.add_argument("--homedir", help='Sets alternate home directory '
                                          'under which the ' +
                                          NcmirToolsConfig.UCONFIG_FILE +
                                          ' is loaded (default ~)',
                        default='~')
    return parser


def run(theargs):
    """Runs ciluploader
    """
    sys.stdout.write("Hello from ciluploader\n")
    return