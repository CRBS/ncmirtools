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
from configparser import NoOptionError
from configparser import NoSectionError

from ncmirtools.config import NcmirToolsConfig
from ncmirtools.kiosk.transfer import Transfer
from ncmirtools.kiosk.transfer import SftpTransfer

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
        t = Transfer(None)
        t.connect()
        t.disconnect()
        msg, duration, bytes_transferred = t.transfer_file('foo')
        self.assertEqual(msg, 'Not implemented')
        self.assertEqual(duration, -1)
        self.assertEqual(bytes_transferred, -1)

    def test_sftptransfer_get_value_from_config(self):
        # test with None for Config
        t = SftpTransfer(None)
        res = t._get_value_from_config(SftpTransfer.SECTION,
                                       SftpTransfer.HOST)
        self.assertEqual(res, None)

        # test with no section
        con = configparser.ConfigParser()
        t = SftpTransfer(con)
        res = t._get_value_from_config(SftpTransfer.SECTION,
                                       SftpTransfer.HOST)
        self.assertEqual(res, None)

        # test with no option
        con.add_section(SftpTransfer.SECTION)
        t = SftpTransfer(con)
        res = t._get_value_from_config(SftpTransfer.SECTION,
                                       SftpTransfer.HOST)
        self.assertEqual(res, None)

        # test valid
        # test with no section
        con.set(SftpTransfer.SECTION,
                SftpTransfer.HOST, 'someval')
        t = SftpTransfer(con)
        res = t._get_value_from_config(SftpTransfer.SECTION,
                                       SftpTransfer.HOST)
        self.assertEqual(res, 'someval')

    def test_sftptransfer_get_private_key(self):
        # test with no option set
        t = SftpTransfer(None)
        res = t._getprivatekey()
        self.assertEqual(res, None)

        # test with valid key
        temp_dir = tempfile.mkdtemp()
        try:
            # test with invalid key
            dkey = os.path.join(temp_dir, 'dummy.key')
            con = configparser.ConfigParser()
            con.add_section(SftpTransfer.SECTION)
            con.set(SftpTransfer.SECTION,
                    SftpTransfer.KEY, dkey)
            t = SftpTransfer(con)

            # test with invalid key
            try:
                t._getprivatekey()
                self.fail('Expected IOError')
            except IOError:
                pass

            # test with valid key
            f = open(dkey, 'w')
            f.write(self._get_dummy_private_key())
            f.flush()
            f.close()
            res = t._getprivatekey()
            self.assertEqual(res.get_name(), 'ssh-rsa')

        finally:
            shutil.rmtree(temp_dir)

    def test_sftptransfer_get_host(self):
        con = configparser.ConfigParser()
        con.add_section(SftpTransfer.SECTION)
        con.set(SftpTransfer.SECTION,
                SftpTransfer.HOST, 'host')
        t = SftpTransfer(con)
        self.assertEqual(t._gethost(), 'host')

    def test_sftptransfer_getusername(self):
        con = configparser.ConfigParser()
        con.add_section(SftpTransfer.SECTION)
        con.set(SftpTransfer.SECTION,
                SftpTransfer.USER, 'user')
        t = SftpTransfer(con)
        self.assertEqual(t._getusername(), 'user')

    def test_sftptransfer_get_missing_host_key_policy(self):
        t = SftpTransfer(None)
        res = t._get_missing_host_key_policy()
        self.assertTrue('AutoAddPolicy' in str(res))

    def test_sftptransfer_getport(self):
        t = SftpTransfer(None)
        self.assertEqual(t._getport(), 22)

        con = configparser.ConfigParser()
        con.add_section(SftpTransfer.SECTION)
        con.set(SftpTransfer.SECTION,
                SftpTransfer.PORT, '23')
        t = SftpTransfer(con)
        self.assertEqual(t._getport(), 23)

    def test_sftptransfer_get_destdir(self):
        con = configparser.ConfigParser()
        con.add_section(SftpTransfer.SECTION)
        con.set(SftpTransfer.SECTION,
                SftpTransfer.DEST_DIR, 'dir')
        t = SftpTransfer(con)
        self.assertEqual(t._getdestdir(), 'dir')

    def test_sftptransfer_getconnecttimeout(self):
        t = SftpTransfer(None)
        self.assertEqual(t._getconnecttimeout(), 60)

        con = configparser.ConfigParser()
        con.add_section(SftpTransfer.SECTION)
        con.set(SftpTransfer.SECTION,
                SftpTransfer.CON_TIMEOUT, '45')
        t = SftpTransfer(con)
        self.assertEqual(t._getconnecttimeout(), 45)

    def test_getdestdir(self):
        t = SftpTransfer(None)
        res = t._getdestdir()
        self.assertEqual(res, None)
        con = configparser.ConfigParser()
        con.add_section(SftpTransfer.SECTION)
        con.set(SftpTransfer.SECTION,
                SftpTransfer.DEST_DIR, '/foo')
        t = SftpTransfer(con)
        res = t._getdestdir()
        self.assertEqual(res, '/foo')

    def test_connect_invalid_connection(self):
        con = configparser.ConfigParser()
        con.add_section(SftpTransfer.SECTION)
        con.set(SftpTransfer.SECTION,
                SftpTransfer.HOST,
                '127.0.0.1')
        con.set(SftpTransfer.SECTION,
                SftpTransfer.PORT,
                '80')
        t = SftpTransfer(con)
        try:
            t.connect()
            self.fail('Expected some error')
        except:
            pass

    def test_connect_alt_ssh_set(self):
        t = SftpTransfer(None)
        t.set_alternate_connection('foo')
        t.connect()
        self.assertEqual(t._ssh, 'foo')

    def test_disconnect_without_connect_call(self):
        t = SftpTransfer(None)
        t.disconnect()
        self.assertEqual(t._sftp, None)
        self.assertEqual(t._ssh, None)

    def test_disconnect_where_both_cause_exceptions(self):
        t = SftpTransfer(None)
        t._sftp = 'foo'
        t._ssh ='hi'
        t.disconnect()
        self.assertEqual(t._sftp, None)
        self.assertEqual(t._ssh, None)


if __name__ == '__main__':
    sys.exit(unittest.main())