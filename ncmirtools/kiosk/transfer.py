# -*- coding: utf-8 -*-

__author__ = 'churas'

import os
import time
import logging
import paramiko
from configparser import NoOptionError
from configparser import NoSectionError

from ncmirtools.config import NcmirToolsConfig


logger = logging.getLogger(__name__)


class Transfer(object):
    """Base object to transfer file to remote server
    """
    def __init__(self, config):
        self._config = config

    def connect(self):
        """Connects to remote server
        """
        logger.debug('placeholder connect() invoked')


    def disconnect(self):
        """Disconnects from remote server
        """
        logger.debug('placeholder disconnect() invoked')

    def transfer_file(self, filepath):
        """Transfers file specified by `filepath` to remote
           server
        :param filepath: path to file to transfer
        :returns tuple (status, time, bytestransferred)
                 where
                 status is None upon success or a string
                        upon error.
                 time is number of seconds it took to transfer
                 bytestransferred is bytes sent
        """
        logger.warning('Subclasses need to implementthis method')
        return 'Not implemented', -1, -1


class SftpTransfer(Transfer):
    """Transfers file to remote server via SFTP
       defined by a `configparser.ConfigParser` passed into
       the constructor with the following values set:

       [`SECTION`]
       `HOST` = <remote host>*
       `USER` = <user name ie bob>
       `PORT` = <port to use ie 22>
       `KEY` = <private key if used>
       `DEST_DIR` = <destination directory on remote host>*

       NOTE: lines above with * are required
    """
    SECTION = 'sftptransfer'
    HOST = 'host'
    USER = 'username'
    PORT = 'port'
    KEY = 'private_key'
    DEST_DIR = 'destination_dir'
    CON_TIMEOUT = 'connect_timeout'

    DEFAULT_PORT = 22
    DEFAULT_CON_TIMEOUT = 60

    def __init__(self, config):
        """Constructor
        :param config: configparser.ConfigParser object set with
                       with values set as described in constructor
                       documentation
        """
        super(SftpTransfer, self).__init__(config)
        self._altssh = None
        self._ssh = None
        self._sftp = None

    def _get_value_from_config(self, section, option):
        """Gets value from configuration
        :param section: section containing option keyword
        :param optionkey: option keyword
        :returns value for keyword or None
        """
        if self._config is None:
            logger.error('Configuration for SftpTransfer is None')
            return None
        try:
            return self._config.get(section, option)
        except NoSectionError:
            logger.info('No section named: ' + str(section))
            return None
        except NoOptionError:
            logger.info('No option named: ' + str(option))
            return None

    def _getprivatekey(self):
        """Gets private key from config
        """
        pkey_file = self._get_value_from_config(SftpTransfer.SECTION,
                                                SftpTransfer.KEY)
        if pkey_file is not None:
            logger.debug('Key file => ' + str(pkey_file))
            return paramiko.RSAKey.from_private_key_file(pkey_file)
        return None

    def _gethost(self):
        return self._get_value_from_config(SftpTransfer.SECTION,
                                           SftpTransfer.HOST)

    def _getusername(self):
        return self._get_value_from_config(SftpTransfer.SECTION,
                                           SftpTransfer.USER)

    def _get_missing_host_key_policy(self):
        return paramiko.AutoAddPolicy()

    def _getport(self):
        val = self._get_value_from_config(SftpTransfer.SECTION,
                                           SftpTransfer.PORT)
        if val is None:
            return SftpTransfer.DEFAULT_PORT

        logger.debug('Using user set port of: ' + str(val))
        return int(val)

    def _getconnecttimeout(self):
        val = self._get_value_from_config(SftpTransfer.SECTION,
                                          SftpTransfer.CON_TIMEOUT)
        if val is None:
            return SftpTransfer.DEFAULT_CON_TIMEOUT
        return int(val)

    def _getdestdir(self):
        return self._get_value_from_config(SftpTransfer.SECTION,
                                           SftpTransfer.DEST_DIR)

    def set_alternate_connection(self, altssh):
        """Sets alternate ssh connection
        :param altssh: Object that is paramiko.SSHClient or one that
                    implements put,close,set_missing_host_key_policy
        """
        self._altssh = altssh

    def connect(self):
        """Connects to remote server as defined by"""
        if self._altssh is not None:
            logger.info('Alternate ssh connection set, using instead')
            self._ssh = self._altssh
            return
        logger.info('Connecting via ssh to ' + str(self._gethost()))
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(self._get_missing_host_key_policy())
        self._ssh.connect(hostname=self._gethost(),
                          username=self._getusername(),
                          pkey=self._getprivatekey(),
                          port=self._getport(),
                          timeout=self._getconnecttimeout())
        logger.debug('Connection completed')

    def disconnect(self):
        """Disconnects
        """
        logger.debug('Disconnecting from ssh server ' +
                     str(self._gethost()))
        if self._sftp is not None:
            try:
                self._sftp.close()
            except Exception:
                logger.error('Caught exception closing sftp connection')
            self._sftp = None
        if self._ssh is not None:
            try:
                self._ssh.close()
            except Exception:
                logger.error('Caught exception closing ssh connection')
            self._ssh = None

    def transfer_file(self, filepath):
        """transfers file
        """
        if self._sftp is None:
            logger.debug('Creating SFTP connection')
            self._sftp = self._ssh.open_sftp()

        dest_dir = self._getdestdir()

        dest_file = os.path.join(dest_dir, os.path.basename(filepath))
        logger.info('Uploading ' + str(filepath) + ' to ' + dest_file)

        transfer_err_msg = None
        start_time = int(time.time())
        bytes_transferred = 0
        try:
            s = self._sftp.put(filepath, dest_file, confirm=True)
            bytes_transferred = s.st_size
        except Exception as e:
            transfer_err_msg = str(e)

        duration = int(time.time()) - start_time

        logger.info('Transfer error message: ' + str(transfer_err_msg) +
                    ', elapsed time in secs ' + str(duration) +
                    ', bytes transferred' +
                    str(bytes_transferred))
        return transfer_err_msg, duration, bytes_transferred