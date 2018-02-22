#! /usr/bin/env python

import os
import sys
import argparse
import logging
import ncmirtools

from ncmirtools.config import NcmirToolsConfig
from ncmirtools.config import ConfigMissingError
from ncmirtools import config
from ncmirtools import ciluploader


# create logger
logger = logging.getLogger('ncmirtools.ncmirtool')



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

    subparsers = parser.add_subparsers(help='sub-command', description='this is something',
                                       dest='subcommand')
    ciluploader._get_argument_parser(subparsers)

    parser.add_argument("--log", dest="loglevel", choices=['DEBUG',
                        'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Set the logging level (default WARNING)",
                        default='WARNING')
    parser.add_argument('--version', action='version',
                        version=('%(prog)s ' + ncmirtools.__version__))

    return parser.parse_args(args, namespace=parsed_arguments)


def main(arglist):
    desc = """
              Version {version}

              """.format(version=ncmirtools.__version__)

    theargs = _parse_arguments(desc, arglist[1:])
    theargs.program = arglist[0]
    theargs.version = ncmirtools.__version__
    config.setup_logging(logger, loglevel=theargs.loglevel)
    try:
        logger.debug('Sub command is: ' + str(theargs.subcommand))
        if theargs.subcommand == 'cilupload':
            logger.debug('Running ciluploader.run ' + str(theargs.subcommand))
            ciluploader.run(theargs)
    finally:
        logging.shutdown()


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
