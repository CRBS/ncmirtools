#! /usr/bin/env python

import os
import sys
import argparse
import ncmirtools
import logging

from ncmirtools.lookup import ProjectSearchViaDatabase
from ncmirtools.config import NcmirToolsConfig
from ncmirtools.config import ConfigMissingError

LOG_FORMAT = "%(asctime)-15s %(levelname)s %(name)s %(message)s"

# create logger
logger = logging.getLogger('ncmirtools.projectsearch')

NO_PROJECTS_FOUND_MSG = 'No matching projects found'

class Parameters(object):
    """Placeholder class for parameters
    """
    pass


def _setup_logging(theargs):
    """hi
    """
    theargs.logformat = LOG_FORMAT
    theargs.numericloglevel = logging.NOTSET
    if theargs.loglevel == 'DEBUG':
        theargs.numericloglevel = logging.DEBUG
    if theargs.loglevel == 'INFO':
        theargs.numericloglevel = logging.INFO
    if theargs.loglevel == 'WARNING':
        theargs.numericloglevel = logging.WARNING
    if theargs.loglevel == 'ERROR':
        theargs.numericloglevel = logging.ERROR
    if theargs.loglevel == 'CRITICAL':
        theargs.numericloglevel = logging.CRITICAL

    logger.setLevel(theargs.numericloglevel)
    logging.basicConfig(format=theargs.logformat)

    logging.getLogger('ncmirtools.config').setLevel(theargs.numericloglevel)
    logging.getLogger('ncmirtools.projectsearch').setLevel(theargs.numericloglevel)
    logging.getLogger('ncmirtools.lookup').setLevel(theargs.numericloglevel)


def _parse_arguments(desc, args):
    """Parses command line arguments using argparse.
    """
    parsed_arguments = Parameters()

    help_formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=help_formatter)
    parser.add_argument("keyword", help='keyword to search for in name or '
                                     ' description of project')
    parser.add_argument("--log", dest="loglevel", choices=['DEBUG',
                        'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Set the logging level (default WARNING)",
                        default='WARNING')
    parser.add_argument("--homedir", help='Sets alternate home directory'
                                          'under which the ' +
                                          NcmirToolsConfig.CONFIG_FILE +
                                          ' is loaded (default ~)',
                        default='~')
    parser.add_argument('--version', action='version',
                        version=('%(prog)s ' + ncmirtools.__version__))

    return parser.parse_args(args, namespace=parsed_arguments)


def _run_search_database(keyword, homedir):
    """Performs search for directory
    :param prefixdir: Directory search path
    :param mpid: microcsopy product id to use to find directory
    :returns: exit code for program
    """
    try:
        config = NcmirToolsConfig()
        config.set_home_directory(os.path.expanduser(homedir))

        search = ProjectSearchViaDatabase(config.get_config())
        res = search.get_matching_projects(keyword)
        if len(res) > 0:
            for entry in res:
                sys.stdout.write(entry + os.linesep)
            return 0

        sys.stderr.write(NO_PROJECTS_FOUND_MSG + os.linesep)
        return 1
    except ConfigMissingError:
        sys.stderr.write('\nERROR: Configuration file missing.\n'
                         ' Please run projectsearch.py --help for '
                         'information on how\n to create a configuration '
                         'file\n\n')
        return 3
    except Exception:
        logger.exception("Error caught exception")
        return 2


def main():
    config = NcmirToolsConfig()
    desc = """
              Version {version}

              Given a <keyword> this script searches the database for any
              projects where the keyword exists in the project name or
              description. The search is case insensitive. The matching
              projects will be output separated by new line characters
              as follows:

              <project id>   <project name>

              If no project matches the <keyword> is found this program will
              output to standard error the message '{projectnotfound}'
              and exit with value 1.

              If there is an unknown error this program will output a message
              and exit with value 2.

              If {config_file}
              is missing then this program will output a message and exit
              with value 3.

              Example Usage:

              projectsearch.py 'yo'
              2033 yo project
              2047 you better believe it

              NOTE:

              This script requires a configuration file which contains
              the information to connect to the database.

              For this account the file should be located here:
              {config_file}

              and should have the following format:

              [{db}]
              {user} = <database username>
              {password} = <database password>
              {port} = <database port ie 5432>
              {host} = <database host>
              {database} = <database name>

              """.format(version=ncmirtools.__version__,
                         projectnotfound=NO_PROJECTS_FOUND_MSG,
                         db=NcmirToolsConfig.POSTGRES_SECTION,
                         user=NcmirToolsConfig.POSTGRES_USER,
                         password=NcmirToolsConfig.POSTGRES_PASS,
                         port=NcmirToolsConfig.POSTGRES_PORT,
                         host=NcmirToolsConfig.POSTGRES_HOST,
                         database=NcmirToolsConfig.POSTGRES_DB,
                         config_file=config.get_config_file())

    theargs = _parse_arguments(desc, sys.argv[1:])
    theargs.program = sys.argv[0]
    theargs.version = ncmirtools.__version__
    _setup_logging(theargs)
    try:
        return _run_search_database(theargs.keyword, theargs.homedir)
    finally:
        logging.shutdown()


if __name__ == '__main__':
    sys.exit(main())
