#! /usr/bin/env python

import os
import sys
import argparse
import ncmirtools
import logging

from ncmirtools.config import NcmirToolsConfig
from ncmirtools.config import ConfigMissingError
from ncmirtools import config
from ncmirtools.kiosk.transfer import SftpTransferFromConfigFactory
from ncmirtools.kiosk.datafinder import SecondYoungestFromConfigFactory


# create logger
logger = logging.getLogger('ncmirtools.imagetokiosk')

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
    parser.add_argument(HOMEDIR_ARG, help='Sets alternate home directory '
                                          'under which the ' +
                                          NcmirToolsConfig.UCONFIG_FILE +
                                          ' is loaded (default ~)')
    parser.add_argument('--version', action='version',
                        version=('%(prog)s ' + ncmirtools.__version__))

    return parser.parse_args(args, namespace=parsed_arguments)


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
        last_trans_file = f.readline().rstrip()
        logger.info('Last transferred file: ' + str(last_trans_file))
        return last_trans_file
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


def _upload_image_file(theargs, thefile, con, alt_transfer=None):
    """Uploads image file and logs it so we don't try to upload
       the same file twice
    """
    last_file = _get_last_transferred_file(con)
    if last_file is None or last_file != thefile:
        if alt_transfer is None:
            logger.debug('Creating SftpTransfer object')
            fac = SftpTransferFromConfigFactory(con)
            transfer, errmsg = fac.get_sftptransfer()
            if transfer is None:
                sys.stderr.write(errmsg + _get_run_help_string(theargs) + '\n')
                return 4
        else:
            logger.debug('Using alternate transfer object passed in')
            transfer = alt_transfer

        try:
            logger.debug('Connecting to remote server')
            transfer.connect()
            size_b = os.path.getsize(thefile)
            sys.stdout.write('\nTransferring ' + str(thefile) +
                             ' which is ' + str(size_b) + ' bytes\n')
            size_b = os.path.getsize(thefile)
            logger.info('File is ' + str(size_b) +
                        ' bytes')

            if theargs.mode == RUN_MODE:
                (status, duration,
                 bytes_transferred) = transfer.transfer_file(thefile)
                logger.info('Status (None means success): ' + str(status) +
                            ', duration: ' + str(duration) +
                            ' seconds, bytes transferred: ' +
                            str(bytes_transferred))

                if status is None:
                    sys.stdout.write('After ' + str(duration) +
                                     ' seconds. Transfer succeeded.\n')
                    logger.debug('Updating transferred file')
                    _update_last_transferred_file(thefile, con)
                    return 0
                else:
                    sys.stdout.write('After ' + str(duration) +
                                     ' seconds. Transfer failed: ' +
                                     str(status) + '\n')
                    return 1

            else:
                sys.stdout.write('File that would have been transferred: ' +
                                 thefile + '\n')

        finally:
            logger.debug('Disconnecting from remote server')
            transfer.disconnect()
    else:
        sys.stdout.write('According to last transfer log, ' +
                         str(thefile) + ' already transferred\n')
    return 0


def _get_file_finder(theargs, con):
    """Gets file finder based on arguments and configuration
       set in `theargs` right now this will always be
       SecondYoungest finder

       :returns: tuple (SecondYoungest, None) upon success or
                 (None, 'error msg as str') upon failure
    """
    fac = SecondYoungestFromConfigFactory(con)
    filefinder, errmsg = fac.get_file_finder()
    if errmsg is not None:
        new_errmsg = errmsg + _get_run_help_string(theargs)
        return None, new_errmsg

    return filefinder, None


def _check_and_transfer_image(theargs):
    """Looks for new image to transfer and sends it
    """
    if theargs.mode == DRYRUN_MODE:
        sys.stdout.write(DRYRUN_MODE.upper() +
                         ' MODE NO CHANGES OR TRANSFERS WILL BE PERFORMED\n')

    con, errmsg = _get_and_verifyconfigparserconfig(theargs)
    if errmsg is not None:
        sys.stderr.write(errmsg + '\n')
        return 2

    filefinder, errmsg = _get_file_finder(theargs, con)
    if errmsg is not None:
        sys.stderr.write(errmsg + '\n')
        return 3

    thefile = filefinder.get_next_file()
    if thefile is None:
        sys.stdout.write('Did not find a file to transfer\n')
        return 0

    return _upload_image_file(theargs, thefile, con)


def _get_run_help_string(theargs):
    """Generates humanreadable string telling user how to run
       program with -h flag to display help information
    :param theargs: object returned from _parse_arguments() which
                    should have theargs.program set to script name
    :returns: human readable string telling user how to invoke help.
              Ex: Please run <program> -h for more information.
    """
    return 'Please run ' + theargs.program + ' -h ' + 'for more information.'


def _get_and_verifyconfigparserconfig(theargs):
    """Loads configuration
    :param theargs: Object with parameters set from _parse_arguments()
                    This method just looks at theargs.homedir and
                    if it is set the value of theargs.homedir is
                    used as the default home directory for loading
                    configuration file
    :returns configparse.ConfigParser object
    """
    config = NcmirToolsConfig()
    try:
        if theargs.homedir is not None:
            logger.info('Setting home directory to: ' + theargs.homedir)
            config.set_home_directory(theargs.homedir)
    except AttributeError:
        logger.debug('Caught AttributeError when examining ' +
                     HOMEDIR_ARG + ' value')
    try:
        con = config.get_config()
    except ConfigMissingError as e:
        return None, str(e)

    if con.has_section(NcmirToolsConfig.DATASERVER_SECTION) is False:
        return None, ('No [' + NcmirToolsConfig.DATASERVER_SECTION +
                      '] section found in configuration. ' +
                      _get_run_help_string(theargs))

    return con, None


def main(arglist):
    con = NcmirToolsConfig()
    desc = """
              Version {version}

              Using a configuration file explained below this script
              looks for the second youngest file under a configuration
              specified directory matching a given suffix.
              That file is then transferred to the remote server if it was
              NOT transferred in the previous invocations of this script.

              The first argument denotes the mode of operation. Currently
              two modes are supported ({run}|{dryrun})

              In "{run}" mode the following line will be output to standard
              out if a file is transferred:

              Transferring /data/21.dm4 which is X bytes

              With the following line output upon success:

              After X seconds. Transfer succeeded.

              Upon failure:

              After X seconds. Transfer failed: (reason for failure):

              or a python stack trace will be output for an uncaught error.


              If file has been transferred then this will be output:

              According to last transfer log, /data/21.dm4 already transferred

              If script could not find the second youngest file:

              Did not find a file to transfer

              In "{dryrun}" mode this script still connects to the remote
              server, but no transfer will be performed and the
              following line will be output to standard out otherwise
              output will match that described in {run} mode:

              {dryrunupper} MODE NO CHANGES OR TRANSFERS WILL BE PERFORMED



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
              {transferlog}  = <file which contains last file transferred,
                                 prevents duplicate transfer of files>

              [{ds_ssh}]

              {ssh_key}      = <path to private ssh key>
              {ssh_user}         = <ssh username>
              {kioskserver}             = <remote kiosk server>
              {kioskdir}  = <remote kiosk directory>


              Example configuration file:

              [{ds}]

              {datadir}          = /cygdrive/e/data
              {imagesuffix}      = .dm4
              {d_exclude}    = $RECYCLE.BIN
              {transferlog}  = /cygdrive/home/foo/last_transferred_file.log

              [{ds_ssh}]

              {ssh_key}      = /cygdrive/home/foo/.ssh/mykey
              {ssh_user}         = foo
              {kioskserver}             = foo.com
              {kioskdir}  = /data

              """.format(version=ncmirtools.__version__,
                         ds=NcmirToolsConfig.DATASERVER_SECTION,
                         datadir=NcmirToolsConfig.DATASERVER_DATADIR,
                         imagesuffix=NcmirToolsConfig.DATASERVER_IMGSUFFIX,
                         d_exclude=NcmirToolsConfig.DATASERVER_DIRSTOEXCLUDE,
                         kioskdir=SftpTransferFromConfigFactory.DEST_DIR,
                         kioskserver=SftpTransferFromConfigFactory.HOST,
                         homedir=HOMEDIR_ARG,
                         transferlog=NcmirToolsConfig.DATASERVER_TRANSFERLOG,
                         ds_ssh=SftpTransferFromConfigFactory.SECTION,
                         ssh_key=SftpTransferFromConfigFactory.KEY,
                         ssh_user=SftpTransferFromConfigFactory.USER,
                         run=RUN_MODE,
                         dryrun=DRYRUN_MODE,
                         dryrunupper=DRYRUN_MODE.upper(),
                         config_file=', '.join(con.get_config_files()))

    theargs = _parse_arguments(desc, arglist[1:])
    theargs.program = arglist[0]
    theargs.version = ncmirtools.__version__
    config.setup_logging(logger, loglevel=theargs.loglevel)
    try:
        return _check_and_transfer_image(theargs)
    finally:
        logging.shutdown()


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
