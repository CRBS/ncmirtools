# -*- coding: utf-8 -*-

__author__ = 'churas'

import os
import time
import logging
import paramiko
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
    """
    def __init__(self, config):
        super(SftpTransfer, self).__init__(config)
        self._altssh = None
        self._ssh = None
        self._sftp = None

    def _get_private_key(self):
        """Gets private key from config
        """
        pkey_file = self._config.get(NcmirToolsConfig.DATASERVER_SSH_SECTION,
                                     NcmirToolsConfig.DATASERVER_SSH_KIOSKKEY)
        return paramiko.RSAKey.from_private_key_file(pkey_file)

    def _get_kioskserver(self):
        return self._config.get(NcmirToolsConfig.DATASERVER_SECTION,
                                NcmirToolsConfig.DATASERVER_KIOSKSERVER)

    def _get_kioskusername(self):
        return self._config.get(NcmirToolsConfig.DATASERVER_SSH_SECTION,
                                NcmirToolsConfig.DATASERVER_SSH_KIOSKUSER)

    def _get_missing_host_key_policy(self):
        return paramiko.AutoAddPolicy()

    def _get_kioskport(self):
        return 22

    def _get_kioskconnecttimeout(self):
        return 60

    def _get_kioskdir(self):
        return self._config.get(NcmirToolsConfig.DATASERVER_SECTION,
                                NcmirToolsConfig.DATASERVER_KIOSKDIR)

    def set_alternate_connection(self, altssh):
        self._altssh = altssh

    def connect(self):
        """Connects to remote server as defined by"""
        if self._altssh is not None:
            logger.info('Alternate ssh connection set, using instead')
            self._ssh = self._altssh
            return
        logger.debug('Connecting via ssh to ' + str(self._get_kioskserver()))
        self._ssh = paramiko.SSHClient()
        self._ssh.connect(hostname=self._get_kioskserver(),
                          username=self._get_kioskusername(),
                          pkey=self._get_private_key(),
                          port=self._get_kioskport(),
                          timeout=self._get_kioskconnecttimeout())
        logger.debug('Connection completed')

    def disconnect(self):
        """Disconnects
        """
        logger.debug('Disconnecting from ssh server ' +
                     str(self._get_kioskserver()))
        if self._sftp is not None:
            self._sftp.close()
            self._sftp = None
        if self._ssh is not None:
            self._ssh.close()
            self._ssh = None

    def transfer_file(self, filepath):
        """transfers file
        """
        if self._sftp is None:
            logger.debug('Creating SFTP connection')
            self._sftp = self._ssh.open_sftp()

        kiosk_dir = self._get_kioskdir()

        dest_file = os.path.join(kiosk_dir, os.path.basename(filepath))
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
                    bytes_transferred)
        return transfer_err_msg, duration, bytes_transferred
