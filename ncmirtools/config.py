__author__ = 'churas'


import os
import configparser
import logging


logger = logging.getLogger(__name__)


def setup_logging(thelogger,
                  log_format='%(asctime)-15s %(levelname)s %(name)s '
                             '%(message)s',
                  loglevel='WARNING'):
    """Sets up logging
    """
    if loglevel == 'DEBUG':
        numericloglevel = logging.DEBUG
    if loglevel == 'INFO':
        numericloglevel = logging.INFO
    if loglevel == 'WARNING':
        numericloglevel = logging.WARNING
    if loglevel == 'ERROR':
        numericloglevel = logging.ERROR
    if loglevel == 'CRITICAL':
        numericloglevel = logging.CRITICAL

    logger.setLevel(numericloglevel)
    thelogger.setLevel(numericloglevel)
    logging.basicConfig(format=log_format)
    logging.getLogger('ncmirtools.projectsearch').setLevel(numericloglevel)
    logging.getLogger('ncmirtools.projectdir').setLevel(numericloglevel)
    logging.getLogger('ncmirtools.mpidir').setLevel(numericloglevel)
    logging.getLogger('ncmirtools.lookup').setLevel(numericloglevel)


class ConfigMissingError(Exception):
    """Raised if configuration file is missing
    """
    pass


class NcmirToolsConfig(object):
    """Class provides access to ncmirtools configuration
    file which is stored in the user's home directory
    """

    CONFIG_FILE = 'ncmirtools.conf'
    UCONFIG_FILE = '.' + CONFIG_FILE
    POSTGRES_SECTION = 'postgres'
    POSTGRES_USER = 'user'
    POSTGRES_PASS = 'password'
    POSTGRES_HOST = 'host'
    POSTGRES_PORT = 'port'
    POSTGRES_DB = 'database'
    ETC_DIR = '/etc'

    def __init__(self):
        """Constructor
        """
        self._homedir = os.path.expanduser('~')
        self._etcdir = NcmirToolsConfig.ETC_DIR

    def set_home_directory(self, path):
        """Sets alternate home directory
        :param path: Alternate home directory path
        """
        self._homedir = path

    def set_etc_directory(self, path):
        """Sets alternate etc directory
        :param path: alternate etc directory path
        """
        self._etcdir = path

    def get_home_directory(self):
        """Returns home directory path
        :returns: Path to home directory
        """
        return self._homedir

    def get_etc_directory(self):
        """Returns etc directory path
        :return: Path to etc directory
        """
        return self._etcdir

    def get_config_files(self):
        """Gets full path to configuration file
        :returns: Full path to configuration file under the home directory
                  of the user
        """
        return [os.path.join(self._etcdir,
                             NcmirToolsConfig.CONFIG_FILE),
                os.path.join(self._homedir,
                             NcmirToolsConfig.UCONFIG_FILE)]

    def get_config(self):
        """Gets configparser object loaded with configuration
        :returns output of configparser.ConfigParser() after it has been
                 loaded with configuration from `get_config_file()`
        :raises ConfigMissingError: If no configuration file is found
        """
        config_exists = False
        for path in self.get_config_files():
            if os.path.isfile(path):
                config_exists = True

        if config_exists is False:
            raise ConfigMissingError('No configuration file found in paths: ' +
                                     ', '.join(self.get_config_files()))

        parser = configparser.ConfigParser()
        parser.read(self.get_config_files())
        return parser
