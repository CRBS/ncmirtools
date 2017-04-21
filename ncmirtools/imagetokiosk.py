#! /usr/bin/env python

import os
import sys
import argparse
import time
import ncmirtools
import logging
import psutil

from ncmirtools.config import NcmirToolsConfig
from ncmirtools import config
from ncmirtools.kiosk.transfer import SftpTransfer

from lockfile.pidlockfile import PIDLockFile


# create logger
logger = logging.getLogger('ncmirtools.imagetokioskdaemon')

HOMEDIR_ARG = '--homedir'
RUN_MODE = 'run'
DRYRUN_MODE = 'dryrun'

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
                        choices=[RUN_MODE, DRYRUN_MODE],
                        help="Sets run mode, " + DRYRUN_MODE +
                             " only goes through the steps"
                             " and " + RUN_MODE +
                             " actually does the transfer")
    parser.add_argument("--log", dest="loglevel", choices=['DEBUG',
                        'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Set the logging level (default WARNING)",
                        default='WARNING')
    """
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
    """
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

       This uses ``PIDLockFile`` to create a pid lock file
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


def _get_files_in_directory_generator(path,
                                      list_of_dirs_to_exclude):
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
            if list_of_dirs_to_exclude is None or \
                            os.path.basename(fullpath) not in \
                            list_of_dirs_to_exclude:
                for aentry in _get_files_in_directory_generator(fullpath,
                                                                list_of_dirs_to_exclude):
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
    file_count = 0
    files_wrong_suffix_count = 0
    start_time = int(time.time())
    for img_file in _get_files_in_directory_generator(searchdir,
                                                      list_of_dirs_to_exclude):

        if suffix is not None and not img_file.endswith(suffix):
            files_wrong_suffix_count += 1
            continue

        file_count += 1
        file_mtime = os.path.getmtime(img_file)
        if file_mtime > curyoungest_file_mtime:
            secondyoungest_file = curyoungest_file
            curyoungest_file = img_file
            curyoungest_file_mtime = file_mtime

    duration = int(time.time()) - start_time
    logger.info('Search took ' + str(duration) + ' seconds. Found ' +
                str(files_wrong_suffix_count) + ' eligible files and ' +
                str(files_wrong_suffix_count) +
                ' files with invalid suffix')
    return secondyoungest_file


def _get_last_transferred_file(con):
    """Gets last transferred file from transferlogfile
    :param con: ConfigParser object which should have
                a value for `NcmirToolsConfig.DATASERVER_SECTION`,
                `NcmirToolsConfig.DATASERVER_TRANSFERLOG`
                that contains path to transfer log file
    :returns: string containing path to last transferred log file or None
              if none was set
    """
    if con is None:
        return None

    tlog = con.get(NcmirToolsConfig.DATASERVER_SECTION,
                   NcmirToolsConfig.DATASERVER_TRANSFERLOG)
    if not os.path.isfile(tlog):
        logger.info('No transfer log found: ' + tlog)
        return None

    f = open(tlog, 'r')
    try:
        return f.readline().rstrip()
    finally:
        f.close()


def _update_last_transferred_file(thefile, con):
    """Updates last transferred file with new file
    :param thefile: path of file to update transfer log file
    :param con: ConfigParser object which should have a value for
                `NcmirToolsConfig.DATASERVER_SECTION`,
                `NcmirToolsConfig.DATASERVER_TRANSFERLOG`
                that contains path to transfer log file
    """
    if con is None:
        logger.error('configuration object passed in is None')
        return

    tlog = con.get(NcmirToolsConfig.DATASERVER_SECTION,
                   NcmirToolsConfig.DATASERVER_TRANSFERLOG)
    try:
        f = open(tlog, 'w')
        f.write(thefile + '\n')
        f.flush()
        f.close()
    except IOError:
        logger.exception('Caught exception trying to write last transfer file')
    except TypeError:
        logger.exception('Problems writing data to logfile: ' + str(thefile))


def _upload_image_file(thefile, mode, con, alt_transfer=None):
    """Uploads image file and logs it so we don't try to upload
       the same file twice
    """
    last_file = _get_last_transferred_file(con)
    if last_file is None or last_file != thefile:
        logger.info('Transferring file')
        if alt_transfer is None:
            logger.debug('Creating SftpTransfer object')
            transfer = SftpTransfer(con)
        else:
            logger.debug('Using alternate transfer object passed in')
            transfer = alt_transfer

        if mode is RUN_MODE:
            logger.debug('Transferring ' + str(thefile))
            transfer.transfer_file(thefile)
            logger.debug('Transfer complete of ' + str(thefile))

            logger.debug('Updating transferred file')
            _update_last_transferred_file(thefile, con)
        else:
            logger.info(DRYRUN_MODE + ' mode')
            sys.stdout.write('File that would have been transferred: ' +
                             thefile + '\n\n')
    else:
        logger.debug('File already transferred')
    return


def _check_and_transfer_image(theargs):
    """Looks for new image to transfer and sends it
    """
    if theargs.mode is DRYRUN_MODE:
        sys.stdout.write('\n' + DRYRUN_MODE +
                         ' NO CHANGES OR TRANSFERS WILL BE PERFORMED\n')

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

        return _upload_image_file(thefile, theargs.mode, con)
    finally:
        if lock is not None:
            lock.release()


def main(arglist):
    con = NcmirToolsConfig()
    desc = """
              Version {version}

              Using a configuration file explained below this script
              looks for the second youngest file matching a given suffix.
              That file is then transferred to the remote server if it was
              NOT transferred in the previous invocation of this script.

              The first argument in this script denotes whether to
              perform the transfer or just output to standard out the
              file that would be transferred.

              NOTE:

              This script requires a configuration file which contains
              information on what data to sync to where

              Unless overriden by {homedir} flag, the configuration file
              is looked for in these paths with values in last path
              taking precedence:

              {config_file}

              The configuration file should have values in this format:

              [{ds}]

              {datadir}          = <directory to monitor>
              {imagesuffix}      = <suffix of images ie .dm4>
              {d_exclude}    = <comma delimited list of directory paths>
              {kioskserver}      = <remote kiosk server>
              {kioskdir}         = <remote kiosk directory>
              {transferlog}  = <file which contains last file transferred,
                                 prevents duplicate transfer of files>
              {lockfile}         = <path to lockfile,
                                   prevents duplicate invocations>

              [{ds_ssh}]

              {ssh_key}  = <path to private ssh key>
              {ssh_user}    = <ssh username>


              Example configuration file:

              [{ds}]

              {datadir}          = /cygdrive/e/data
              {imagesuffix}      = .dm4
              {d_exclude}    = $RECYCLE.BIN
              {kioskserver}      = foo.com
              {kioskdir}         = /data
              {transferlog}  = /cygdrive/home/foo/transfer.log
              {lockfile}         = /cygdrive/home/foo/mylockfile.pid

              [{ds_ssh}]

              {ssh_key}  = /cygdrive/home/foo/.ssh/mykey
              {ssh_user}    = foo

              """.format(version=ncmirtools.__version__,
                         ds=NcmirToolsConfig.DATASERVER_SECTION,
                         datadir=NcmirToolsConfig.DATASERVER_DATADIR,
                         imagesuffix=NcmirToolsConfig.DATASERVER_IMGSUFFIX,
                         d_exclude=NcmirToolsConfig.DATASERVER_DIRSTOEXCLUDE,
                         kioskdir=NcmirToolsConfig.DATASERVER_KIOSKDIR,
                         kioskserver=NcmirToolsConfig.DATASERVER_KIOSKSERVER,
                         lockfile=NcmirToolsConfig.DATASERVER_LOCKFILE,
                         homedir=HOMEDIR_ARG,
                         transferlog=NcmirToolsConfig.DATASERVER_TRANSFERLOG,
                         ds_ssh=NcmirToolsConfig.DATASERVER_SSH_SECTION,
                         ssh_key=NcmirToolsConfig.DATASERVER_SSH_KIOSKKEY,
                         ssh_user=NcmirToolsConfig.DATASERVER_SSH_KIOSKUSER,
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
