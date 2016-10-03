#! /usr/bin/env python

import sys
import argparse
import ncmirtools
import logging

from ncmirtools.lookup import DirectoryForMicroscopyProductId

LOG_FORMAT = "%(asctime)-15s %(levelname)s %(name)s %(message)s"

# create logger
logger = logging.getLogger('ncmirtools.mpidir')

DIR_NOT_FOUND_MSG = 'Directory not found'

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

    logging.getLogger('ncmirtools.mpidir').setLevel(theargs.numericloglevel)
    logging.getLogger('ncmirtools').setLevel(theargs.numericloglevel)


def _parse_arguments(desc, args):
    """Parses command line arguments using argparse.
    """
    parsed_arguments = Parameters()

    help_formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=help_formatter)
    parser.add_argument("mpid", help='Microscopy id')
    parser.add_argument("--log", dest="loglevel", choices=['DEBUG',
                        'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Set the logging level (default WARNING)",
                        default='WARNING')

    parser.add_argument('--prefixdir',
                        default=DirectoryForMicroscopyProductId.PROJECT_DIR,
                        help='Defines the search path. <VOLUME_ID> and '
                             '<PROJECT_ID>'
                             'can be any value and <MP_ID> is the '
                             'value that'
                             'will be matched to the mpid value set on the '
                             'command line. (default ' +
                             DirectoryForMicroscopyProductId.PROJECT_DIR)

    parser.add_argument('--version', action='version',
                        version=('%(prog)s ' + ncmirtools.__version__))

    return parser.parse_args(args, namespace=parsed_arguments)


def _run_lookup(prefixdir, mpid):
    """Performs search for directory
    :param prefixdir: Directory search path
    :param mpid: microcsopy product id to use to find directory
    :returns: exit code for program
    """
    try:
        dmp = DirectoryForMicroscopyProductId(prefixdir)
        mp_dirs = dmp.get_directory_for_microscopy_product_id(mpid)
        if len(mp_dirs) > 0:
            for entry in mp_dirs:
                print entry
            return 0

        sys.stderr.write(DIR_NOT_FOUND_MSG + '\n')
        return 1
    except Exception:
        logger.exception("Error caught exception")
        return 2


def main():
    desc = """
              Version {version}

              Outputs the directory, or directories where the given
              (mpid) or Microscopy id resides on the filesystem.

              If multiple directories match they will be output separated by
              newline character.

              If no path matching (mpid) is found this program will output
              to standard error the message '{dirnotfound}' and
              exit with value 1.

              If there is an error this program will output a message and
              exit with value 2.

              """.format(version=ncmirtools.__version__,
                         dirnotfound=DIR_NOT_FOUND_MSG)

    theargs = _parse_arguments(desc, sys.argv[1:])
    theargs.program = sys.argv[0]
    theargs.version = ncmirtools.__version__
    _setup_logging(theargs)
    sys.exit(_run_lookup(theargs.prefixdir, theargs.mpid))


if __name__ == '__main__':
    main()
