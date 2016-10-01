#!python

import sys
import os
import argparse
import ncmirtools
import re

import logging

LOG_FORMAT = "%(asctime)-15s %(levelname)s %(name)s %(message)s"

# create logger
logger = logging.getLogger('ncmirtools.mpidir')


VOLUME_ID='<VOLUME_ID>'
MP_ID='<MP_ID>'
PROJECT_ID='<PROJECT_ID>'

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



def _split_search_paths(initial_path):
    """splits path
    """
    return re.split('^(.*)'+VOLUME_ID+'(.*)'+PROJECT_ID+'(.*)'+MP_ID, initial_path)


def _get_list_of_dirs_matching_prefix(thedir, theprefix,exactmatch=False):
    """hi
    """
    matching_dirs = []

    logger.debug("thedir=" + thedir + " theprefix="+theprefix)

    for entry in os.listdir(thedir):
        if exactmatch is False:
            if entry.startswith(theprefix):
                # print 'found match'
                matching_dirs.append(os.path.join(thedir, entry))
        else:
            if entry == theprefix:
                 matching_dirs.append(os.path.join(thedir, entry))
    return matching_dirs

def _find_directory_for_microscopy_id(theargs):
    """Looks for
    """
    splitpath = _split_search_paths(theargs.prefixdir)
    logger.debug(splitpath)
    splitpath[2] = re.sub('^/','',splitpath[2])
    splitpath[3] = re.sub('^/','',splitpath[3])

    basedir = os.path.dirname(splitpath[1])
    dirprefix = os.path.basename(splitpath[1])
    match_vol_dirs = _get_list_of_dirs_matching_prefix(basedir, dirprefix)
    logger.debug('vol dir count ' + str(len(match_vol_dirs)))
    project_dir_count = 0
    mp_dir_count = 0
    final_matches = []
    for vol_dir in match_vol_dirs:
        # print 'vol dir ' + vol_dir
        raw_prj_dir = os.path.join(vol_dir, splitpath[2])
        # print 'raw_prj_dir ' + raw_prj_dir
        basedir = os.path.dirname(raw_prj_dir)
        dirprefix = os.path.basename(raw_prj_dir)
        match_prj_dirs = _get_list_of_dirs_matching_prefix(basedir, dirprefix)
        project_dir_count += len(match_prj_dirs)

        for mp_dir in match_prj_dirs:
            raw_mp_dir = os.path.join(mp_dir, splitpath[3])
            basedir = os.path.dirname(raw_mp_dir)
            dirprefix = os.path.basename(raw_mp_dir) + str(theargs.mpid)
            match_mp_dirs = _get_list_of_dirs_matching_prefix(basedir, dirprefix, exactmatch=True)
            mp_dir_count += len(match_mp_dirs)
            if len(match_mp_dirs) > 0:
                final_matches.extend(match_mp_dirs)

    logger.debug('project dir count ' + str(project_dir_count))
    logger.debug('mp_dir count ' + str(mp_dir_count))

    return final_matches


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
    pdir = ('/ccdbprod/ccdbprod<VOLUME_ID>/home'
            '/CCDB_DATA_USER.portal/CCDB_DATA_USER'
            '/acquisition/project_<PROJECT_ID>'
            '/microscopy_<MP_ID>')
    parser.add_argument('--prefixdir',
                        default=pdir,
                        help='Defines the search path. <VOLUME_ID> and '
                             '<PROJECT_ID>'
                             'can be any value and <MP_ID> is the '
                             'value that'
                             'will be matched to the mpid value set on the '
                             'command line. (default ' + pdir)

    parser.add_argument('--version', action='version',
                        version=('%(prog)s ' + ncmirtools.__version__))

    return parser.parse_args(args, namespace=parsed_arguments)


def main():
    desc = """
              Version {version}

              Outputs the directory where the given (mpid) or Microscopy id
              resides on the filesystem.
              """.format(version=ncmirtools.__version__)

    theargs = _parse_arguments(desc, sys.argv[1:])
    theargs.program = sys.argv[0]
    theargs.version = ncmirtools.__version__
    _setup_logging(theargs)

    try:
        mp_dirs = _find_directory_for_microscopy_id(theargs)
        if len(mp_dirs) > 0:
            for entry in mp_dirs:
                print entry

    except Exception:
        logger.exception("Error caught exception")
        sys.exit(2)


if __name__ == '__main__':
    main()
