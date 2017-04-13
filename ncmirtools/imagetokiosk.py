#! /usr/bin/env python

import os
import sys
import argparse
import ncmirtools
import logging
import psutil

from ncmirtools.config import NcmirToolsConfig
from ncmirtools import config

from lockfile.pidlockfile import PIDLockFile


# create logger
logger = logging.getLogger('ncmirtools.imagetokioskdaemon')

HOMEDIR_ARG = '--homedir'

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

    parser.add_argument("mode",
                        choices=['run', 'dryrun'],
                        help="Sets run mode dryrun only goes through the steps"
                             " and run actually does the transfer")
    parser.add_argument("--log", dest="loglevel", choices=['DEBUG',
                        'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Set the logging level (default WARNING)",
                        default='WARNING')
    parser.add_argument("--" + NcmirToolsConfig.DATASERVER_DATADIR,
                        help='Data directory to examine '
                             'this overrides value in ' +
                             NcmirToolsConfig.UCONFIG_FILE)
    parser.add_argument("--" + NcmirToolsConfig.DATASERVER_IMGSUFFIX,
                        help='Suffix to use to determine what '
                             'images to transfer, overrides value in ' +
                             NcmirToolsConfig.UCONFIG_FILE)
    parser.add_argument("--" + NcmirToolsConfig.DATASERVER_DIRSTOEXCLUDE,
                        help='Comma list of directories to not examine, '
                             ' overrides value in ' +
                             NcmirToolsConfig.UCONFIG_FILE)
    parser.add_argument("--" + NcmirToolsConfig.DATASERVER_LOCKFILE,
                        help='Path to lockfile,'
                             ' overrides value in ' +
                             NcmirToolsConfig.UCONFIG_FILE)
    parser.add_argument(HOMEDIR_ARG, help='Sets alternate home directory '
                                          'under which the ' +
                                          NcmirToolsConfig.UCONFIG_FILE +
                                          ' is loaded (default ~)',
                        default='~')
    parser.add_argument('--version', action='version',
                        version=('%(prog)s ' + ncmirtools.__version__))

    return parser.parse_args(args, namespace=parsed_arguments)


def _get_lock(lockfile):
    """Create lock file to prevent this process from running on same data.

       This uses ``PIDLockFile`` to create a pid lock file in latest_weekly
       directory named celprunner.<stage>.lockpid
       If pid exists it is assumed the lock is held otherwise lock
       is broken and recreated

       :param lockfile: lockfile path
       :return: ``PIDLockFile`` upon success
       :raises: LockException: If there was a problem locking
       :raises: Exception: If valid pid lock file already exists
       """

    logger.debug("Looking for lock file: " + lockfile)
    lock = PIDLockFile(lockfile, timeout=10)

    if lock.i_am_locking():
        logger.debug("My process id" + str(lock.read_pid()) +
                     " had the lock so I am breaking")
        lock.break_lock()
        lock.acquire(timeout=10)
        return lock

    if lock.is_locked():
        logger.debug("Lock file exists checking pid")
        if psutil.pid_exists(lock.read_pid()):
            raise Exception("imagetokiosk.py with pid " +
                            str(lock.read_pid()) +
                            " is running")

    lock.break_lock()
    logger.info("Acquiring lock")
    lock.acquire(timeout=10)
    return lock


def _get_files_in_directory_generator(self, path):
    """Generator that gets files in directory"""

    if path is None:
        logger.error('Path is None, returning nothing')
        return

    # first time we encounter a file yield it
    if os.path.isfile(path):
        yield path

    # second time we encounter a file just return
    if os.path.isfile(path):
        return

    if not os.path.isdir(path):
        return

    logger.debug(path + ' is a directory looking for files within')
    for entry in os.listdir(path):
        fullpath = os.path.join(path, entry)
        if os.path.isfile(fullpath):
            yield fullpath
        if os.path.isdir(fullpath):
            for aentry in self._get_files_in_directory_generator(fullpath):
                yield aentry


def _get_second_youngest_image_file(searchdir, suffix, list_of_dirs_to_exclude):
    """Looks for 2nd youngest file in `searchdir` directory path
    :param searchdir: directory to examine
    :param suffix: Only consider files with this suffix
    :param list_of_dirs_to_exclude: List of directory paths to
                                    exclude using endswith match on directory
    """
    if searchdir is None:
        logger.error('searchdir is none')
        return None

    curyoungest_file = None
    curyoungest_file_mtime = 0
    secondyoungest_file = None
    # walk through all files in file system skipping files that
    # do NOT match `suffix`
    # Also exclude any paths
    for img_file in _get_files_in_directory_generator(searchdir):
        if not img_file.endswith(suffix):
            continue
        file_mtime = os.path.getmtime(img_file)
        if file_mtime > curyoungest_file_mtime:
            secondyoungest_file = curyoungest_file
            curyoungest_file = img_file
            curyoungest_file_mtime = file_mtime

    return secondyoungest_file


def _upload_image_file(thefile, con):
    """hi
    """
    return


def _check_and_transfer_image(theargs):
    """Looks for new image to transfer and sends it
    """
    config = NcmirToolsConfig()
    try:
        if theargs.homedir is not None:
            logger.debug('Setting home directory to: ' + theargs.homedir)
            config.set_home_directory(theargs.homedir)
    except AttributeError:
        logger.debug('Caught AttributeError when examining ' +
                     HOMEDIR_ARG + ' value')

    con = config.get_config()
    lockfile = con.get(NcmirToolsConfig.DATASERVER_SECTION,
                       NcmirToolsConfig.DATASERVER_LOCKFILE)
    lock = _get_lock(lockfile)
    try:
        datadir = con.get(NcmirToolsConfig.DATASERVER_SECTION,
                          NcmirToolsConfig.DATASERVER_DATADIR)
        thefile = _get_second_youngest_image_file(datadir)
        if thefile is None:
            logger.info('Could not find second youngest file')
            return

        return _check_and_transfer_image(thefile, con)
    finally:
        if lock is not None:
            lock.release()


def main(arglist):
    con = NcmirToolsConfig()
    desc = """
              Version {version}

              This script examines directory set by --{datadir} for the
              second youngest image file with value set in --{imagesuffix}. If
              found this file is then uploaded to --{kioskserver} and
              put in --{kioskdir} directory.

              NOTE:

              This script requires a configuration file which contains
              information on what data to sync to where

              Unless overriden by --{homedir} flag, the configuration file
              is looked for in these paths with values in last path
              taking precedence:

              {config_file}

              The configuration file should have values in this format:

              [{ds}]
              {datadir}       = <directory to monitor>
              {imagesuffix}   = <suffix of images ie .dm4>
              {d_exclude} = <comma delimited list of directory paths>
              {kioskserver}   = <remote kiosk server>
              {kioskdir}      = <remote kiosk directory>
              {lockfile}      = <path to lockfile,
                                prevents duplicate invocations>

              Example configuration file:

              [{ds}]
              {datadir}       = /cygdrive/e/data
              {imagesuffix}   = .dm4
              {d_exclude} = $RECYCLE.BIN
              {kioskserver}   = foo.com
              {kioskdir}      = /data
              {lockfile}      = /cygdrive/home/foo/mylockfile.pid

              """.format(version=ncmirtools.__version__,
                         ds=NcmirToolsConfig.DATASERVER_SECTION,
                         datadir=NcmirToolsConfig.DATASERVER_DATADIR,
                         imagesuffix=NcmirToolsConfig.DATASERVER_IMGSUFFIX,
                         d_exclude=NcmirToolsConfig.DATASERVER_DIRSTOEXCLUDE,
                         kioskdir=NcmirToolsConfig.DATASERVER_KIOSKDIR,
                         kioskserver=NcmirToolsConfig.DATASERVER_KIOSKSERVER,
                         lockfile=NcmirToolsConfig.DATASERVER_LOCKFILE,
                         homedir=HOMEDIR_ARG,
                         config_file=', '.join(con.get_config_files()))

    theargs = _parse_arguments(desc, arglist[1:])
    theargs.program = arglist[0]
    theargs.version = ncmirtools.__version__
    config.setup_logging(logger, loglevel=theargs.loglevel)
    try:
        _check_and_transfer_image(theargs)
    finally:
        logging.shutdown()


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))