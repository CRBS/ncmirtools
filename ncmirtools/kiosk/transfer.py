# -*- coding: utf-8 -*-

__author__ = 'churas'

import os
import time
import logging
import paramiko


logger = logging.getLogger(__name__)


class InvalidDestinationDirError(Exception):
    """Error raised when destination directory is invalid
    """
    pass


class SSHConnectionError(Exception):
    """Error raised when ssh connection is invalid
    """
    pass


class Transfer(object):
    """Base object to transfer file to remote server
    """
    def __init__(self):
        pass

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


class SftpTransferFromConfigFactory(object):
    """Creates SftpTransfer objects from configparser.ConfigParser
       object
    """
    SECTION = 'sftptransfer'
    HOST = 'host'
    USER = 'username'
    PORT = 'port'
    KEY = 'private_key'
    DEST_DIR = 'destination_dir'
    CON_TIMEOUT = 'connect_timeout'

    def __init__(self, config):
        """Constructor
           defined by a `configparser.ConfigParser` passed into
           the constructor with the following values set:

           [sftptransfer]
           host = <remote host>*
           username = <user name ie bob>
           port = <port to use ie 22>
           private_key = <private key if used>
           destination_dir = <destination directory on remote host>*

           NOTE: lines above with * are required
        :param config: configparser.ConfigParser object used
                       to create SftpTransfer object
        """
        self._config = config

    def get_sftptransfer(self):
        """Gets `SftpTransfer` object using values from
           `configparser.ConfigParser` passed into constructor
        :returns: tuple (SftpTransfer, None) upon success or
                  (None, 'error message as str') upon failure
        """
        con = self._config
        if con is None:
            return None, ('No configuration passed into ' +
                          'SftpTransferFromConfigFactory')

        if con.has_section(SftpTransferFromConfigFactory.SECTION) is False:
            return None, ('No [' + SftpTransferFromConfigFactory.SECTION +
                          '] section found in configuration.')

        if con.has_option(SftpTransferFromConfigFactory.SECTION,
                          SftpTransferFromConfigFactory.HOST) is False:
            return None, ('No ' + SftpTransferFromConfigFactory.HOST +
                          ' option found in configuration.')

        host = con.get(SftpTransferFromConfigFactory.SECTION,
                       SftpTransferFromConfigFactory.HOST)

        if con.has_option(SftpTransferFromConfigFactory.SECTION,
                          SftpTransferFromConfigFactory.DEST_DIR) is False:
            return None, ('No ' + SftpTransferFromConfigFactory.DEST_DIR +
                          ' option found in configuration.')

        destdir = con.get(SftpTransferFromConfigFactory.SECTION,
                          SftpTransferFromConfigFactory.DEST_DIR)

        if con.has_option(SftpTransferFromConfigFactory.SECTION,
                          SftpTransferFromConfigFactory.USER) is True:
            user = con.get(SftpTransferFromConfigFactory.SECTION,
                           SftpTransferFromConfigFactory.USER)
        else:
            user = None

        if con.has_option(SftpTransferFromConfigFactory.SECTION,
                          SftpTransferFromConfigFactory.PORT) is True:
            port = int(con.get(SftpTransferFromConfigFactory.SECTION,
                               SftpTransferFromConfigFactory.PORT))
        else:
            port = None

        if con.has_option(SftpTransferFromConfigFactory.SECTION,
                          SftpTransferFromConfigFactory.KEY) is True:
            pkey = con.get(SftpTransferFromConfigFactory.SECTION,
                           SftpTransferFromConfigFactory.KEY)
        else:
            pkey = None

        if con.has_option(SftpTransferFromConfigFactory.SECTION,
                          SftpTransferFromConfigFactory.CON_TIMEOUT) is True:
            con_time = int(con.get(SftpTransferFromConfigFactory.SECTION,
                                   SftpTransferFromConfigFactory.CON_TIMEOUT))
        else:
            con_time = None

        return SftpTransfer(host, destdir, username=user,
                            port=port, privatekeyfile=pkey,
                            connect_timeout=con_time), None


class SftpTransfer(Transfer):
    """Transfers file to remote server via SFTP
    """
    DEFAULT_PORT = 22
    DEFAULT_CONTIMEOUT = 60

    def __init__(self, host, destdir, username=None,
                 port=22, privatekeyfile=None, connect_timeout=60,
                 missing_host_key_policy=None,
                 passphrase=None):
        """Constructor
        :param config: configparser.ConfigParser object set with
                       with values set as described in constructor
                       documentation
        """
        super(SftpTransfer, self).__init__()
        self._host = host
        self._destdir = destdir
        self._username = username
        if port is None:
            self._port = SftpTransfer.DEFAULT_PORT
        else:
            self._port = port

        if privatekeyfile is not None:
            self._pkey = paramiko.RSAKey.from_private_key_file(privatekeyfile,
                                                               passphrase)
        else:
            self._pkey = None

        if connect_timeout is None:
            self._connect_timeout = SftpTransfer.DEFAULT_CONTIMEOUT
        else:
            self._connect_timeout = connect_timeout

        self._missing_host_key_policy = paramiko.AutoAddPolicy()
        self._altssh = None
        self._ssh = None
        self._sftp = None
        self._passphrase = passphrase

    def get_host(self):
        """Gets host
        """
        return self._host

    def get_destination_directory(self):
        """Gets destination directory
        """
        return self._destdir

    def get_private_key(self):
        """Gets private key object
        """
        return self._pkey

    def get_connect_timeout(self):
        """Gets connect timeout
        """
        return self._connect_timeout

    def get_port(self):
        """Gets port
        """
        return self._port

    def get_username(self):
        """Gets username
        """
        return self._username

    def get_passphrase(self):
        """Gets passphrase
        """
        return self._passphrase

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
        start_time = int(time.time())
        logger.info('Connecting via ssh to ' + str(self._host))
        self._ssh = paramiko.SSHClient()
        if self._missing_host_key_policy is not None:
            self._ssh.set_missing_host_key_policy(self.
                                                  _missing_host_key_policy)

        self._ssh.connect(hostname=self._host,
                          username=self._username,
                          pkey=self._pkey,
                          port=self._port,
                          passphrase=self._passphrase,
                          timeout=self._connect_timeout)
        logger.info('Connection completed, took ' +
                    str(int(time.time()) - start_time) + ' seconds.')

    def disconnect(self):
        """Disconnects
        """
        logger.debug('Disconnecting from ssh server ' +
                     str(self._host))
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
            if self._ssh is None:
                raise SSHConnectionError('ssh connection never set.'
                                         ' connect() must be called '
                                         'first')
            self._sftp = self._ssh.open_sftp()

        if self._destdir is None:
            raise InvalidDestinationDirError('Destination directory '
                                             'cannot be None')

        dest_file = self._destdir + '/' + os.path.basename(filepath)
        logger.info('Uploading ' + str(filepath) + ' to ' + dest_file)

        transfer_err_msg = None
        start_time = int(time.time())
        bytes_transferred = 0
        try:
            s = self._sftp.put(filepath, dest_file, confirm=True)
            bytes_transferred = s.st_size
        except Exception as e:
            logger.exception('Caught exception performing sftp put')
            transfer_err_msg = ('Caught an exception: ' +
                                str(e.__class__.__name__) + ' : ' + str(e))

        duration = int(time.time()) - start_time

        logger.info('Transfer error message: ' + str(transfer_err_msg) +
                    ', elapsed time in secs ' + str(duration) +
                    ', bytes transferred ' +
                    str(bytes_transferred))
        return transfer_err_msg, duration, bytes_transferred
