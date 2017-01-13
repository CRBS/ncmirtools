#! /usr/bin/env python

import os
import sys
import argparse
import ncmirtools
import logging

from ncmirtools.lookup import MicroscopyProductLookupViaDatabase
from ncmirtools.config import NcmirToolsConfig
from ncmirtools.config import ConfigMissingError
from ncmirtools import config


# create logger
logger = logging.getLogger('ncmirtools.mpidinfo')

NO_MICROSCOPY_PRODUCT_FOUND_MSG = 'No matching Microscopy Product found'


class Parameters(object):
    """Placeholder class for parameters
    """
    pass


def _parse_arguments(desc, args):
    """Parses command line arguments using argparse.
    """
    parsed_arguments = Parameters()

    help_formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=help_formatter)
    parser.add_argument("mpid", help='Microscopy product id (must be'
                                     'an int less then 2^31)',
                        type=int)
    parser.add_argument("--log", dest="loglevel", choices=['DEBUG',
                        'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Set the logging level (default WARNING)",
                        default='WARNING')
    parser.add_argument("--homedir", help='Sets alternate home directory '
                                          'under which the ' +
                                          NcmirToolsConfig.UCONFIG_FILE +
                                          ' is loaded (default ~)',
                        default='~')
    parser.add_argument('--version', action='version',
                        version=('%(prog)s ' + ncmirtools.__version__))

    return parser.parse_args(args, namespace=parsed_arguments)


def _run_search_database(mpid, homedir):
    """Performs search for directory
    :param prefixdir: Directory search path
    :param mpid: microscopy product id to use to find directory
    :returns: exit code for program
    """
    try:
        config = NcmirToolsConfig()
        config.set_home_directory(os.path.expanduser(homedir))

        search = MicroscopyProductLookupViaDatabase(config.get_config())
        res = search.get_microscopyproduct_for_id(mpid)
        if res is not None:
            sys.stdout.write(res.get_as_string())
            return 0

        sys.stderr.write(NO_MICROSCOPY_PRODUCT_FOUND_MSG + os.linesep)
        return 1
    except ConfigMissingError:
        sys.stderr.write('\nERROR: Configuration file missing.\n'
                         ' Please run mpidinfo.py --help for '
                         'information on how\n to create a configuration '
                         'file\n\n')
        return 3
    except Exception:
        logger.exception("Error caught exception")
        return 2


def main(arglist):
    con = NcmirToolsConfig()
    desc = """
              Version {version}

              Given a <mpid> this script searches the database for
              a Microscopy Product that has this <mpid>.
              The matching Microscopy Product will be output in this format

              Id: <mpid>

              Image Basename:

                 <image basename>

              Notes:

                 <notes>

              If no Microscopy Product matches the <mpid> is found this
              program will output to standard error the message
              '{mpnotfound}'
              and exit with value 1.

              If there is an unknown error this program will output a message
              and exit with value 2.

              If {config_file}
              is missing then this program will output a message and exit
              with value 3.

              Example Usage:

              mpidinfo.py 123

              Id: 123

              Image Basename:

                 foo

              Notes:

                 some notes


              NOTE:

              This script requires a configuration file which contains
              the information to connect to the database.

              For this account the file should be located in one of these
              paths:

              {config_file}

              and should have the following format:

              [{db}]
              {user} = <database username>
              {password} = <database password>
              {port} = <database port ie 5432>
              {host} = <database host>
              {database} = <database name>

              """.format(version=ncmirtools.__version__,
                         mpnotfound=NO_MICROSCOPY_PRODUCT_FOUND_MSG,
                         db=NcmirToolsConfig.POSTGRES_SECTION,
                         user=NcmirToolsConfig.POSTGRES_USER,
                         password=NcmirToolsConfig.POSTGRES_PASS,
                         port=NcmirToolsConfig.POSTGRES_PORT,
                         host=NcmirToolsConfig.POSTGRES_HOST,
                         database=NcmirToolsConfig.POSTGRES_DB,
                         config_file=', '.join(con.get_config_files()))

    theargs = _parse_arguments(desc, arglist[1:])
    theargs.program = arglist[0]
    theargs.version = ncmirtools.__version__
    config.setup_logging(logger, loglevel=theargs.loglevel)
    try:
        return _run_search_database(theargs.mpid, theargs.homedir)
    finally:
        logging.shutdown()


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
