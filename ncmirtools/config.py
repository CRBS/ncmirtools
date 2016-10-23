__author__ = 'churas'


import os
import configparser
import logging


logger = logging.getLogger(__name__)


class NcmirToolsConfig(object):
    """Class provides access to ncmirtools configuration
    file which is stored in the user's home directory
    """
    CONFIG_FILE = '.ncmirtools.conf'

    POSTGRES_SECTION = 'postgres'
    POSTGRES_USER = 'user'
    POSTGRES_PASS = 'password'
    POSTGRES_HOST = 'host'
    POSTGRES_PORT = 'port'
    POSTGRES_DB = 'database'

    def __init__(self):
        """Constructor
        """
        self._homedir = os.path.expanduser('~')

    def set_home_directory(self, path):
        """Sets alternate home directory
        :param path: Alternate home directory path
        """
        self._homedir = path

    def get_home_directory(self):
        """Returns home directory path
        :returns: Path to home directory
        """
        return self._homedir

    def get_config_file(self):
        """Gets full path to configuration file
        :returns: Full path to configuration file under the home directory
                  of the user
        """
        return os.path.join(self._homedir,
                            NcmirToolsConfig.CONFIG_FILE)

    def get_config(self):
        """Gets configparser object loaded with configuration
        :returns output of configparser.ConfigParser() after it has been
                 loaded with configuration from `get_config_file()`
        """
        if not os.path.isfile(self.get_config_file()):
            logger.warning('Configuration is not a file')
            return configparser.ConfigParser()

        parser = configparser.ConfigParser()
        parser.read(self.get_config_file())
        return parser
