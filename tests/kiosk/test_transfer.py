#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_transfer
----------------------------------

Tests for `transfer` module.
"""

import shutil
import tempfile
import sys
import unittest
import os
import configparser
from mock import Mock

from ncmirtools.imagetokiosk import Parameters
from ncmirtools.kiosk.transfer import InvalidDestinationDirError
from ncmirtools.kiosk.transfer import SSHConnectionError

from ncmirtools.kiosk.transfer import Transfer
from ncmirtools.kiosk.transfer import SftpTransfer
from ncmirtools.kiosk.transfer import SftpTransferFromConfigFactory


class TestTransfer(unittest.TestCase):

    def _get_dummy_private_key(self):
        return """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAyWp165X5cb3gC53VqnY8++aXyk8D14Bgt2ob1uTd1nYrE5IU
3J3mqU9wvBsx80Xj8syWNmltH6iHH72z7j1nJi3fzbYAD7s3f3cBc8rx3XlM62xA
Cta6aef1TU0VVxLk/VmoHqtqd85dOqlM67Wc/C+Khw0GjhmAuzyMCis/MQtj2ncx
+gt0RnkrZIG2XI3RefbOtOVI7DL8nCjup0y5b4dsZbyI/Za+3bTw0S2JNSEkrylX
MgWM/QdOfPC4TI8ij7hEYI1x+U5nFFQCis5wRV1Da53bHqUAQaWz9ysYm6SRVgaJ
pG+hxyWgxMyqD81B8KK2qNbv8GTQZp96fBD15QIDAQABAoIBAGHXkYjrxcz3C8sY
1R6FaYKEtd/VGmypNFJk/Tka3Ji9tpc/M1soaVB+AqmeHFms7dqYf6/W7ueeGmXU
5X8p3N2zEzD+5HC/5WnKCa6SO4P21OLYJxQc01l3ELaIZ4Fw8EQSNZUQeBvS538D
lxY5lxT6kzSfozuML/jEpNKbx4quvQqF1NwtiOTJPDOHWozyUQhNcsTOYrucuV4j
dCsY6tku47qR+8eaWkfK+EWmBisYlfSlJgP77orXd5lnhTZJkCTnjNB8SKlYXCvi
B99u15FLjmS8QtPbq5NuW8gEFuMajNNWxdXFlMhTlK+mQ+cNlmlt4CUaLqbFHcTI
4buIylECgYEA6re+ftA3ARSi1wac24yxJFugFIuLm4Vq2aACvFcm3+dD8RjpK51u
V97EvAQyCz3eZlAhw5mx8w99QeHnLTtbvU8aFns3t+9XjMOi8D8PWqB7LVEPet/y
uEYT+DaVyeIuXGWE0EYUjFp2ZWz47TMqaAtcgRRaAhhUPlsnrJA9OGsCgYEA2623
AAVuo76zvpGmmVqldygxhRqDVaPFTFusFIpC0IqZAClNSGQxhaG2645vet54vW20
N04TDuvZu+3ea9pOIxoFxLdtQxzFwc27G96GYs5yehHZrWhMMcvSMrYAhZJvKcuV
sGPkkV9dhmPNBNYQAcF48+ha7s0ha6gnXz0WXu8CgYBnpMlWYATZ0k3xmzbqb57N
CjSOvevgubIr9M8gcW92ET3cGX7kxniyDmlbCJM8iY5KKXovUA/W33EVBXa6b2qc
FnDTmodJDkPfoYeyhHX4M8MQiKnIPVmFa1RoF1pfMiP8ostZ2Ig8TbnYIZ1tyFki
ZlnrmZwBLtMMUd4cAfk2jwKBgQCLmLJHsywBpfe2y/ugS/gF5mbBfH2k+DMyOLb7
PnkC6HAdqCFSNUk67+67dYHmBGWZipMQ6e42dy2fvKKwysMIj0rHHQCzux737vJN
3XRsaWBZreozxalVo33pd7qRJuK5HoP62R+wOXfHJLhtsFHvq7Be3nKaeYQZU3vh
i4IhxQKBgQDlJEb+0ZnDlsB1UcMHhXtsO31WrNOn9SiGnDVMc0ik0pBs/06ZIQ/4
Zb8O2Nm8VTNZARdKHN1ll7GT6kNAr6Ae9lc2oEB/EdODZ3ARtUJF1HNxxgl+hwfN
U+27XptJXHsIBqoIbIbx+/TVejFlv8Lp46SdtvgKPXY2pZhtn+3icQ==
-----END RSA PRIVATE KEY-----"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_transfer_base_class(self):
        t = Transfer()
        t.connect()
        t.disconnect()
        msg, duration, bytes_transferred = t.transfer_file('foo')
        self.assertEqual(msg, 'Not implemented')
        self.assertEqual(duration, -1)
        self.assertEqual(bytes_transferred, -1)

    def test_sftptransferfromconfigfactory_get_sftptransfer(self):
        # no config
        fac = SftpTransferFromConfigFactory(None)
        sftp, errmsg = fac.get_sftptransfer()
        self.assertEqual(sftp, None)
        self.assertEqual(errmsg, 'No configuration passed into '
                                 'SftpTransferFromConfigFactory')

        # no section
        con = configparser.ConfigParser()
        fac = SftpTransferFromConfigFactory(con)
        sftp, errmsg = fac.get_sftptransfer()
        self.assertEqual(sftp, None)
        self.assertEqual(errmsg, ('No [' +
                                  SftpTransferFromConfigFactory.SECTION +
                                  '] section found in configuration.'))

        # no host
        con.add_section(SftpTransferFromConfigFactory.SECTION)
        fac = SftpTransferFromConfigFactory(con)
        sftp, errmsg = fac.get_sftptransfer()
        self.assertEqual(sftp, None)
        self.assertEqual(errmsg, ('No ' +
                                  SftpTransferFromConfigFactory.HOST +
                                  ' option found in configuration.'))

        # no dest dir
        con.set(SftpTransferFromConfigFactory.SECTION,
                SftpTransferFromConfigFactory.HOST, 'somehost')
        fac = SftpTransferFromConfigFactory(con)
        sftp, errmsg = fac.get_sftptransfer()
        self.assertEqual(sftp, None)
        self.assertEqual(errmsg, ('No ' +
                                  SftpTransferFromConfigFactory.DEST_DIR +
                                  ' option found in configuration.'))

        # valid with no user, pkey, port
        con.set(SftpTransferFromConfigFactory.SECTION,
                SftpTransferFromConfigFactory.DEST_DIR, '/foo')
        fac = SftpTransferFromConfigFactory(con)
        sftp, errmsg = fac.get_sftptransfer()
        self.assertEqual(sftp.__class__.__name__, 'SftpTransfer')
        self.assertEqual(sftp.get_host(), 'somehost')
        self.assertEqual(sftp.get_port(), SftpTransfer.DEFAULT_PORT)
        self.assertEqual(sftp.get_connect_timeout(),
                         SftpTransfer.DEFAULT_CONTIMEOUT)
        self.assertEqual(sftp.get_destination_directory(), '/foo')
        self.assertEqual(sftp.get_private_key(), None)
        self.assertEqual(sftp.get_username(), None)
        self.assertEqual(errmsg, None)

        # valid with user, pkey, port, and timeout
        temp_dir = tempfile.mkdtemp()
        try:
            con.set(SftpTransferFromConfigFactory.SECTION,
                    SftpTransferFromConfigFactory.PORT, '50')
            con.set(SftpTransferFromConfigFactory.SECTION,
                    SftpTransferFromConfigFactory.USER, 'bob')
            con.set(SftpTransferFromConfigFactory.SECTION,
                    SftpTransferFromConfigFactory.CON_TIMEOUT, '25')
            keyfile = os.path.join(temp_dir, 'somekey')
            f = open(keyfile, 'w')
            f.write(self._get_dummy_private_key())
            f.flush()
            f.close()
            con.set(SftpTransferFromConfigFactory.SECTION,
                    SftpTransferFromConfigFactory.KEY,
                    keyfile)
            fac = SftpTransferFromConfigFactory(con)
            sftp, errmsg = fac.get_sftptransfer()
            self.assertEqual(sftp.get_host(), 'somehost')
            self.assertEqual(sftp.get_port(), 50)
            self.assertEqual(sftp.get_connect_timeout(), 25)
            self.assertEqual(sftp.get_destination_directory(), '/foo')
            self.assertEqual(sftp.get_private_key().get_name(), 'ssh-rsa')
            self.assertEqual(sftp.get_username(), 'bob')
            self.assertEqual(errmsg, None)
        finally:
            shutil.rmtree(temp_dir)

    def test_connect_invalid_connection(self):
        sftp = SftpTransfer('127.0.0.1', '/foo', port=80)
        try:
            sftp.connect()
            self.fail('Expected some error')
        except Exception:
            pass

    def test_connect_alt_ssh_set(self):
        sftp = SftpTransfer('127', '/foo')
        sftp.set_alternate_connection('foo')
        sftp.connect()
        self.assertEqual(sftp._ssh, 'foo')

    def test_disconnect_without_connect_call(self):

        t = SftpTransfer('127', '/foo')
        t._sftp = Parameters()
        t._ssh = Parameters()
        t.disconnect()
        self.assertEqual(t._sftp, None)
        self.assertEqual(t._ssh, None)

    def test_disconnect_where_both_cause_exceptions(self):
        t = SftpTransfer('127', '/foo')
        t._sftp = 'foo'
        t._ssh = 'hi'
        t.disconnect()
        self.assertEqual(t._sftp, None)
        self.assertEqual(t._ssh, None)

    def test_transfer_file_before_connect(self):
        t = SftpTransfer('127', '/foo')
        try:
            t.transfer_file('/foo/hi.txt')
            self.fail('Expected SSHConnectionError')
        except SSHConnectionError:
            pass

    def test_transfer_dest_dir_is_none(self):
        t = SftpTransfer('127', None)
        t._sftp = 'hi'
        try:
            t.transfer_file('/somefile')
            self.fail('Expected InvalidDestinationDirError')
        except InvalidDestinationDirError:
            pass

    def test_transfer_raises_exception(self):
        t = SftpTransfer('127', '/remotedir')
        t._sftp = Parameters()
        t._sftp.put = Mock(side_effect=IOError('some error'))

        msg, dur, b_trans = t.transfer_file('/foo')
        # TODO for some reason in python3 the exception is OSError
        # TODO instead of IOError. Need to figure out what is wrong
        self.assertTrue('Caught an exception: ' in msg)
        self.assertTrue('Error : some error' in msg)

    def test_transfer_success_with_sftp_set(self):
        t = SftpTransfer('127', '/remotedir')
        t._sftp = Parameters()
        mockstat = Parameters()
        mockstat.st_size = 500
        t._sftp.put = Mock(return_value=mockstat)

        msg, dur, b_trans = t.transfer_file('/foo')
        self.assertEqual(msg, None)
        self.assertTrue(dur >= 0)
        self.assertEqual(b_trans, 500)

    def test_transfer_success_with_sftp_created_from_ssh(self):
        t = SftpTransfer('127', '/remotedir')
        mockssh = Parameters()
        mocksftp = Parameters()
        mockstat = Parameters()
        mockstat.st_size = 1500
        mocksftp.put = Mock(return_value=mockstat)
        mockssh.open_sftp = Mock(return_value=mocksftp)
        t.set_alternate_connection(mockssh)
        t.connect()
        msg, dur, b_trans = t.transfer_file('/foo')
        self.assertEqual(msg, None)
        self.assertTrue(dur >= 0)
        self.assertEqual(b_trans, 1500)
        t.disconnect()


if __name__ == '__main__':
    sys.exit(unittest.main())
