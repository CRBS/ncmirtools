#! /usr/bin/env python

import sys
import logging


from ncmirtools.kiosk.transfer import SftpTransfer
from ncmirtools.config import NcmirToolsConfig
from ncmirtools.config import ConfigMissingError


# create logger
logger = logging.getLogger(__name__)


HOMEDIR_ARG = '--homedir'


def _get_argument_parser(subparsers):
    """Parses command line arguments using argparse.
    """
    con = NcmirToolsConfig()
    desc = """
         This tool uploads data to Cell Image Library (CIL) and registers
         it with the CIL. This tool then outputs an ID registered with
         the CIL upon success.
        
         When run this script will output the following to standard out 
         for a successful run with a zero exit code:
         
         CIL id: <id from CIL>
         
         Upon failure a non-zero exit code will be returned and log
         messages will be output at ERROR level denoting the problems.
         
         NOTE: 
         
         This script requires a configuration file which contains
         information on what data to sync to where

         Unless overriden by {homedir} flag, the configuration file
         is looked for in these paths with values in last path
         taking precedence:

         {config_file}

         The configuration file should have values in this format:
         
         [ciluploader]
         
         private_key      = <path to private ssh key>
         username         = <ssh username>
         host             = <remote CIL server>
         destination_dir  = <remote CIL directory>

    """.format(config_file=', '.join(con.get_config_files()),
               homedir=HOMEDIR_ARG)
    parser = subparsers.add_parser('cilupload',
                                   help='Uploads data to Cell Image '
                                        'Library (CIL)',
                                   description=desc)

    parser.add_argument("data", help='Data file to upload, can be an image or movie')
    parser.add_argument("json", help='JSON meta data file')
    parser.add_argument("--homedir", help='Sets alternate home directory '
                                          'under which the ' +
                                          NcmirToolsConfig.UCONFIG_FILE +
                                          ' is loaded (default ~)',
                        default='~')
    return parser


def _get_run_help_string(theargs):
    """Generates humanreadable string telling user how to run
       program with -h flag to display help information
    :param theargs: object returned from _parse_arguments() which
                    should have theargs.program set to script name
    :returns: human readable string telling user how to invoke help.
              Ex: Please run <program> -h for more information.
    """
    return 'Please run ' + theargs.program + ' -h ' + 'for more information.'


def _get_and_verifyconfigparserconfig(theargs):
    """Loads configuration
    :param theargs: Object with parameters set from _parse_arguments()
                    This method just looks at theargs.homedir and
                    if it is set the value of theargs.homedir is
                    used as the default home directory for loading
                    configuration file
    :returns configparse.ConfigParser object
    """
    config = NcmirToolsConfig()
    try:
        if theargs.homedir is not None:
            logger.info('Setting home directory to: ' + theargs.homedir)
            config.set_home_directory(theargs.homedir)
    except AttributeError:
        logger.debug('Caught AttributeError when examining ' +
                     HOMEDIR_ARG + ' value')
    try:
        con = config.get_config()
    except ConfigMissingError as e:
        return None, str(e)

    if con.has_section(CILUploaderFromConfigFactory.CONFIG_SECTION) is False:
        return None, ('No [' + CILUploaderFromConfigFactory.CONFIG_SECTION +
                      '] section found in configuration. ' +
                      _get_run_help_string(theargs))

    return con, None


class CILUploader(object):
    """Uploads and registers data with Cell Image Library"""
    def __init__(self, transfer_obj):
        """Constructor
        """
        self._transfer = transfer_obj

    def upload_and_register_data(self, data):
        """Uploads and registers data to CIL
        """
        # self._transfer.transfer_file(data)
        pass


class CILUploaderFromConfigFactory(object):
    """Creates CILUploader object
    """
    CONFIG_SECTION = 'ciluploader'
    PRIVATE_KEY = 'private_key'
    USERNAME = 'username'
    HOST = 'host'
    DEST_DIR = 'destination_dir'

    def __init__(self, con):
        """Constructor
        :param con: configparser object from NcmirToolsConfig.get_config()
        """
        self._config = con

    def get_ciluploader(self):
        """Creates CILUploader object from configuration passed into
           constructor
        """
        return CILUploader(self._get_sftptransfer_from_config())
    
    def _get_sftptransfer_from_config(self):
        """Gets sftp"""
        con = self._config
        if con is None:
            return None, ('No configuration passed into ' +
                          'CILUploaderFromConfigFactory')

        if con.has_section(CILUploaderFromConfigFactory.CONFIG_SECTION) is False:
            return None, ('No [' + CILUploaderFromConfigFactory.CONFIG_SECTION +
                          '] section found in configuration.')

        if con.has_option(CILUploaderFromConfigFactory.CONFIG_SECTION,
                          CILUploaderFromConfigFactory.HOST) is False:
            return None, ('No ' + CILUploaderFromConfigFactory.HOST +
                          ' option found in configuration.')

        host = con.get(CILUploaderFromConfigFactory.CONFIG_SECTION,
                       CILUploaderFromConfigFactory.HOST)

        if con.has_option(CILUploaderFromConfigFactory.CONFIG_SECTION,
                          CILUploaderFromConfigFactory.DEST_DIR) is False:
            return None, ('No ' + CILUploaderFromConfigFactory.DEST_DIR +
                          ' option found in configuration.')

        destdir = con.get(CILUploaderFromConfigFactory.CONFIG_SECTION,
                          CILUploaderFromConfigFactory.DEST_DIR)

        if con.has_option(CILUploaderFromConfigFactory.CONFIG_SECTION,
                          CILUploaderFromConfigFactory.USER) is True:
            user = con.get(CILUploaderFromConfigFactory.CONFIG_SECTION,
                           CILUploaderFromConfigFactory.USER)
        else:
            user = None

        if con.has_option(CILUploaderFromConfigFactory.CONFIG_SECTION,
                          CILUploaderFromConfigFactory.PORT) is True:
            port = int(con.get(CILUploaderFromConfigFactory.CONFIG_SECTION,
                               CILUploaderFromConfigFactory.PORT))
        else:
            port = None

        if con.has_option(CILUploaderFromConfigFactory.CONFIG_SECTION,
                          CILUploaderFromConfigFactory.KEY) is True:
            pkey = con.get(CILUploaderFromConfigFactory.CONFIG_SECTION,
                           CILUploaderFromConfigFactory.KEY)
        else:
            pkey = None

        if con.has_option(CILUploaderFromConfigFactory.CONFIG_SECTION,
                          CILUploaderFromConfigFactory.CON_TIMEOUT) is True:
            con_time = int(con.get(CILUploaderFromConfigFactory.CONFIG_SECTION,
                                   CILUploaderFromConfigFactory.CON_TIMEOUT))
        else:
            con_time = None

        return SftpTransfer(host, destdir, username=user,
                            port=port, privatekeyfile=pkey,
                            connect_timeout=con_time), None


def run(theargs):
    """Runs ciluploader
    """
    sys.stdout.write("Hello from ciluploader\n")
    con = _get_and_verifyconfigparserconfig(theargs)
    fac = CILUploaderFromConfigFactory(con)
    uploader = fac.get_ciluploader()
    uploader.upload_and_register_data(theargs.data)

    return