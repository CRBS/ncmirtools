#! /usr/bin/env python

import os
import sys
import logging
import argparse
import requests
import json
from requests.auth import HTTPBasicAuth


from ncmirtools.kiosk.transfer import SftpTransfer
from ncmirtools.config import NcmirToolsConfig
from ncmirtools.config import ConfigMissingError


# create logger
logger = logging.getLogger(__name__)


HOMEDIR_ARG = '--homedir'


def get_argument_parser(subparsers):
    """Parses command line arguments using argparse.
    """
    con = NcmirToolsConfig()
    desc = """
         This tool uploads a file to the Cell Image Library (CIL).
         This tool then outputs an ID registered with the CIL upon success.

         When run this script will output the following to standard out
         for a successful run with a zero exit code:

         Success: True
         Id: <CIL Id>
         Destination path: <Path on remote server where file was uploaded>
         Bytes transferred: <Number bytes transferred>
         Duration in seconds: <Number of seconds transfer took>
         Error Message: <'None' upon success otherwise an error message>

         Upon failure a non-zero exit code will be returned and log
         messages will be output at ERROR level denoting the problems along
         with an Exception.

         WARNING: This implementation does not check if file has been uploaded
                  already and will proceed to overwrite the file on the remote
                  server and request a new CIL id via the REST service.

         NOTE:

         This script requires a configuration file which contains
         information on what data to sync to where

         Unless overriden by {homedir} flag, the configuration file
         is looked for in these paths with values in last path
         taking precedence:

         {config_file}

         The configuration file should have values in this format:

         [{config_sect}]

         {pkey}             = <path to private ssh key>
         {pkpass}  = <private ssh key passphrase>
         {user}                = <ssh username>
         {host}                    = <remote CIL server>
         {dest}         = <remote CIL directory>
         {resturl}                 = <REST url service>
         {restuser}            = <user login for rest service>
         {restpass}            = <user password for rest service>

         NOTE: If private key does not need a password just comment out
               or omit {pkpass} parameter from configuration.

               Also note, if private key password is put in configuration
               file be sure to restrict read access.

               Example: For Linux if file is in home directory:
               chmod 0600 ~/.ncmirtools.conf

         Example:

         [{config_sect}]

         {pkey}             = /home/foo/.ssh/mykey
         {pkpass}  = 12345
         {user}                = ciluploader
         {host}                    = cilupload.foo.invalid
         {dest}         = /home/ciluploader/uploads
         {resturl}                 = http://cilrest.crbs.ucsd.edu
         {restuser}            = cilrestuser
         {restpass}            = 67890


    """.format(config_file=', '.join(con.get_config_files()),
               homedir=HOMEDIR_ARG,
               config_sect=CILUploaderFromConfigFactory.CONFIG_SECTION,
               user=CILUploaderFromConfigFactory.USERNAME,
               host=CILUploaderFromConfigFactory.HOST,
               dest=CILUploaderFromConfigFactory.DEST_DIR,
               pkey=CILUploaderFromConfigFactory.PRIVATE_KEY,
               pkpass=CILUploaderFromConfigFactory.PRIVATE_KEY_PASS,
               resturl=CILUploaderFromConfigFactory.REST_URL,
               restuser=CILUploaderFromConfigFactory.REST_USER,
               restpass=CILUploaderFromConfigFactory.REST_PASS)
    help_formatter = argparse.RawDescriptionHelpFormatter

    parser = subparsers.add_parser('cilupload',
                                   help='Uploads data to Cell Image '
                                        'Library (CIL)',
                                   description=desc,
                                   formatter_class=help_formatter)

    parser.add_argument("data", help='Data file to upload, can be any file')
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
    progname = 'Unknown'
    try:
        progname = theargs.program
    except AttributeError:
        pass

    return 'Please run ' + progname + ' -h ' + 'for more information.'


def _get_and_verifyconfigparserconfig(theargs, altconfig=None):
    """Loads configuration
    :param theargs: Object with parameters set from _parse_arguments()
                    This method just looks at theargs.homedir and
                    if it is set the value of theargs.homedir is
                    used as the default home directory for loading
                    configuration file
    :returns configparse.ConfigParser object
    """
    if altconfig is not None:
        config = altconfig
    else:
        config = NcmirToolsConfig()

    if theargs.homedir is not None:
        logger.info('Setting home directory to: ' + theargs.homedir)
        config.set_home_directory(theargs.homedir)

    try:
        con = config.get_config()
    except ConfigMissingError as e:
        return None, str(e)

    if con.has_section(CILUploaderFromConfigFactory.CONFIG_SECTION) is False:
        return None, ('No [' + CILUploaderFromConfigFactory.CONFIG_SECTION +
                      '] section found in configuration. ' +
                      _get_run_help_string(theargs))

    return con, None


class CILUploaderResult(object):
    """Contains result from upload of data by CILUploaderResult
    """
    def __init__(self, success_status, errmsg=None,
                 id=None, bytes_transferred=None,
                 duration=None, dest_path=None):
        """Constructor
        """
        self._success_status = success_status
        self._errmsg = errmsg
        self._id = id
        self._duration = duration
        self._dest_path = dest_path
        self._bytes_transferred = bytes_transferred

    def get_bytes_transferred(self):
        """Gets bytes transferred
        """
        return self._bytes_transferred

    def get_success_status(self):
        """Gets True for success, or False/None otherwise
        """
        return self._success_status

    def set_success_status(self, status):
        self._success_status = status

    def get_error_message(self):
        """Gets error message or None
        """
        return self._errmsg

    def set_error_message(self, errmsg):
        self._errmsg = errmsg

    def get_id(self):
        """Gets id obtained from service
        """
        return self._id

    def set_id(self, id):
        """Sets id
        """
        self._id = id

    def get_destination_path(self):
        """Gets path of file on remote server
        """
        return self._dest_path

    def get_duration(self):
        """Gets duration"""
        return self._duration

    def as_string(self):
        """Gets string representation of object
        """
        val = 'Success: ' + str(self._success_status) + '\n'
        val += 'Id: ' + str(self._id) + '\n'
        val += 'Destination path: ' + str(self._dest_path) + '\n'
        val += 'Bytes transferred: ' + str(self._bytes_transferred) + '\n'
        val += 'Duration in seconds: ' + str(self._duration) + '\n'
        val += 'Error Message: ' + str(self._errmsg) + '\n'
        return val


class CILUploader(object):
    """Uploads and registers data with Cell Image Library"""
    def __init__(self, transfer_obj, resturl=None, restuser=None,
                 restpassword=None):
        """Constructor
        """
        self._transfer = transfer_obj
        self._url = resturl
        self._user = restuser
        self._pass = restpassword

    def upload_and_register_data(self, data,
                                 session=None):
        """Uploads and registers data to CIL
        """
        if self._transfer is None:
            return CILUploaderResult(False,
                                     errmsg='Transfer object was none, '
                                     'cannot complete transfer')

        if self._url is None:
            return CILUploaderResult(False,
                                     errmsg='REST url is None')

        if self._user is None:
            return CILUploaderResult(False,
                                     errmsg='REST username is None')

        if self._pass is None:
            return CILUploaderResult(False,
                                     errmsg='REST password is None')

        if data is None:
            return CILUploaderResult(False,
                                     errmsg='File to transfer is None')

        result = self._upload(data)

        if result.get_success_status() is False:
            return result

        return self._register_data(result, session=session)

    def _upload(self, data):
        """Uploads data to remote server
        :returns CILUploaderResult object with success set to True
        """
        self._transfer.connect()
        (transfer_err_msg, duration,
         bytes_transferred) = self._transfer.transfer_file(data)
        self._transfer.disconnect()

        if transfer_err_msg is not None:
            return CILUploaderResult(False,
                                     errmsg='Error trying to upload: ' +
                                     str(transfer_err_msg))

        logger.info(data + ' file took ' +
                    str(duration) + ' seconds to transfer ' +
                    str(bytes_transferred) + ' bytes')
        dest_f = (self._transfer.get_destination_directory() + '/' +
                  os.path.basename(data))

        return CILUploaderResult(True, bytes_transferred=bytes_transferred,
                                 duration=duration,
                                 dest_path=dest_f)

    def _register_data(self, result,
                       session=None):

        close_session = False
        if session is None:
            close_session = True
            session = requests.Session()
        try:
            r = session.post(self._url + '/upload_rest/upload_entry',
                             json={'File_path': result.get_destination_path()},
                             auth=HTTPBasicAuth(self._user, self._pass))
            success = False
            if r.status_code is 200:
                success = True
                res_dict = json.loads(r.text)
                if res_dict['success'] is True:
                    result.set_success_status(True)
                    result.set_id(res_dict['ID'])
                else:
                    result.set_success_status(False)
                    result.set_error_message('REST response: ' + r.text)
            else:
                result.set_error_message('REST returned error status code: ' +
                                         str(r.status_code))
            result.set_success_status(success)
            return result

        finally:
            if close_session is True:
                session.close()


class CILUploaderFromConfigFactory(object):
    """Creates CILUploader object
    """
    CONFIG_SECTION = 'ciluploader'
    PRIVATE_KEY = 'private_key'
    PRIVATE_KEY_PASS = 'private_key_passphrase'
    USERNAME = 'username'
    HOST = 'host'
    DEST_DIR = 'destination_dir'
    CON_TIMEOUT = '30'
    PORT = '22'
    REST_URL = 'resturl'
    REST_USER = 'restusername'
    REST_PASS = 'restpassword'

    def __init__(self, con):
        """Constructor
        :param con: configparser object from NcmirToolsConfig.get_config()
        """
        self._config = con

    def get_ciluploader(self):
        """Creates CILUploader object from configuration passed into
           constructor
        """
        if self._config is None:
            logger.error('No configuration to parser')
            return None

        uploader, err = self._get_sftptransfer_from_config()
        if uploader is None:
            logger.error('Unable to initialize transfer: ' + str(err))
            return None

        resturl, restuser, restpass, errmsg = self._get_rest_info_from_config()
        if errmsg is not None:
            logger.error('Unable to get rest info from config: ' + errmsg)
            return None

        return CILUploader(uploader, resturl=resturl, restuser=restuser,
                           restpassword=restpass)

    def _get_rest_info_from_config(self):
        """Gets rest configuration information
        """
        con = self._config

        if con.has_section(CILUploaderFromConfigFactory.
                           CONFIG_SECTION) is False:
            return (None, None, None,
                    ('No [' + CILUploaderFromConfigFactory.CONFIG_SECTION +
                     '] section found in configuration.'))

        if con.has_option(CILUploaderFromConfigFactory.CONFIG_SECTION,
                          CILUploaderFromConfigFactory.REST_URL) is False:
            return None, None, None, ('No ' +
                                      CILUploaderFromConfigFactory.REST_URL +
                                      ' option found in configuration.')
        rest_url = con.get(CILUploaderFromConfigFactory.CONFIG_SECTION,
                           CILUploaderFromConfigFactory.REST_URL)

        if con.has_option(CILUploaderFromConfigFactory.CONFIG_SECTION,
                          CILUploaderFromConfigFactory.REST_USER) is False:
            return None, None, None, ('No ' +
                                      CILUploaderFromConfigFactory.REST_USER +
                                      ' option found in configuration.')
        rest_user = con.get(CILUploaderFromConfigFactory.CONFIG_SECTION,
                            CILUploaderFromConfigFactory.REST_USER)

        if con.has_option(CILUploaderFromConfigFactory.CONFIG_SECTION,
                          CILUploaderFromConfigFactory.REST_PASS) is False:
            return None, None, None, ('No ' +
                                      CILUploaderFromConfigFactory.REST_PASS +
                                      ' option found in configuration.')
        rest_pass = con.get(CILUploaderFromConfigFactory.CONFIG_SECTION,
                            CILUploaderFromConfigFactory.REST_PASS)

        return rest_url, rest_user, rest_pass, None

    def _get_sftptransfer_from_config(self):
        """Gets sftp"""
        con = self._config

        if con.has_section(CILUploaderFromConfigFactory.
                           CONFIG_SECTION) is False:
            return None, ('No [' +
                          CILUploaderFromConfigFactory.CONFIG_SECTION +
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
                          CILUploaderFromConfigFactory.USERNAME) is True:
            user = con.get(CILUploaderFromConfigFactory.CONFIG_SECTION,
                           CILUploaderFromConfigFactory.USERNAME)
        else:
            user = None

        if con.has_option(CILUploaderFromConfigFactory.CONFIG_SECTION,
                          CILUploaderFromConfigFactory.PORT) is True:
            port = int(con.get(CILUploaderFromConfigFactory.CONFIG_SECTION,
                               CILUploaderFromConfigFactory.PORT))
        else:
            port = None

        if con.has_option(CILUploaderFromConfigFactory.CONFIG_SECTION,
                          CILUploaderFromConfigFactory.PRIVATE_KEY) is True:
            pkey = con.get(CILUploaderFromConfigFactory.CONFIG_SECTION,
                           CILUploaderFromConfigFactory.PRIVATE_KEY)
        else:
            pkey = None

        if con.has_option(CILUploaderFromConfigFactory.CONFIG_SECTION,
                          CILUploaderFromConfigFactory.CON_TIMEOUT) is True:
            con_time = int(con.get(CILUploaderFromConfigFactory.CONFIG_SECTION,
                                   CILUploaderFromConfigFactory.CON_TIMEOUT))
        else:
            con_time = None

        if con.has_option(CILUploaderFromConfigFactory.CONFIG_SECTION,
                          CILUploaderFromConfigFactory.
                          PRIVATE_KEY_PASS) is True:
            passk = con.get(CILUploaderFromConfigFactory.CONFIG_SECTION,
                            CILUploaderFromConfigFactory.PRIVATE_KEY_PASS)
        else:
            passk = None

        return SftpTransfer(host, destdir, username=user,
                            port=port, privatekeyfile=pkey,
                            connect_timeout=con_time,
                            passphrase=passk), None


def run(theargs):
    """Runs ciluploader
    """
    con, err = _get_and_verifyconfigparserconfig(theargs)
    if con is None:
        logger.error('No configuration: ' + str(err))
        return 1
    fac = CILUploaderFromConfigFactory(con)
    uploader = fac.get_ciluploader()
    if uploader is not None:
        res = uploader.upload_and_register_data(theargs.data)
        if res.get_error_message() is not None:
            logger.error(res.get_error_message())
        if res.get_success_status() is False:
            return 2
        sys.stdout.write(res.as_string() + '\n')
        return 0
    return 3
