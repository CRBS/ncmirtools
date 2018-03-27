# -*- coding: utf-8 -*-

__author__ = 'churas'

import os
import time
import logging

from ncmirtools.config import NcmirToolsConfig

logger = logging.getLogger(__name__)


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
               os.path.basename(fullpath) not in list_of_dirs_to_exclude:
                for aentry in \
                    _get_files_in_directory_generator(fullpath,
                                                      list_of_dirs_to_exclude):
                    yield aentry


class FileFinder(object):
    """Base class for classes that find
       data
    """
    def __init__(self):
        """Constructor"""
        pass

    def get_next_file(self):
        """Gets next found file
        """
        raise NotImplementedError('Should be implemented by subclasses')


class SecondYoungest(FileFinder):
    """Finds second youngest file under a given
    directory tree
    """

    def __init__(self, searchdir, suffix, list_of_dirs_to_exclude):
        """Constructor
        :param searchdir: directory to examine
        :param suffix: Only consider files with this suffix
        :param list_of_dirs_to_exclude: List of directory paths to
                                        exclude using endswith match on
                                        directory
        """
        super(SecondYoungest, self).__init__()
        self._searchdir = searchdir
        self._suffix = suffix
        self._list_of_dirs_to_exclude = list_of_dirs_to_exclude

    def get_searchdir(self):
        """Gets searchdir
        """
        return self._searchdir

    def get_suffix(self):
        """Gets suffix
        """
        return self._suffix

    def get_list_of_directories_to_exclude(self):
        """Gets list of directories to exclude
        """
        return self._list_of_dirs_to_exclude

    def get_next_file(self):
        """Gets 2nd youngest file under searchdir set in
           constructor with suffix matching that constructor
           and not in list_of_dirs_to_exclude set in constructor
        :returns: string path to second youngest file or None
                  if one does not exist.
        """

        if self._searchdir is None:
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
        ex_list = self._list_of_dirs_to_exclude
        for img_file in _get_files_in_directory_generator(self._searchdir,
                                                          ex_list):

            if self._suffix is not None and not img_file.endswith(self.
                                                                  _suffix):
                files_wrong_suffix_count += 1
                continue

            if secondyoungest_file is None:
                secondyoungest_file = img_file

            file_count += 1
            file_mtime = os.path.getmtime(img_file)
            if file_mtime > curyoungest_file_mtime:
                secondyoungest_file = curyoungest_file
                curyoungest_file = img_file
                curyoungest_file_mtime = file_mtime

        duration = int(time.time()) - start_time
        logger.info('Search took ' + str(duration) + ' seconds. Found ' +
                    str(file_count) + ' eligible files and ' +
                    str(files_wrong_suffix_count) +
                    ' files with invalid suffix')
        return secondyoungest_file


class SecondYoungestFromConfigFactory(object):
    """Factory that creates SecondYoungestFileFinder
       from `configparser.ConfigParser` object
    """
    def __init__(self, config):
        self._config = config

    def get_file_finder(self):
        """Parses config passed in constructor to extract
           information needed to create SecondYoungestFileFinder
           object. The configuration must be under the dataserver
           section and the only required option is
           datadir which should be set to directory to examine:
           ex:
           [dataserver]
           datadir = /foo

           Other optional parameters are:

           imagesuffix  = <only include files with suffix ie .dm4>
           dirstoexclude = <comma delimited list of directories to exclude>

        :returns tuple either (SecondYoungestFileFinder, None) upon success or
                              (None, 'error message as str') if there was an
                              error
        """

        # setting con to make the lines below shorter
        con = self._config
        if con is None:
            return None, ('No configuration passed into ' +
                          'SecondYoungestFromConfigFactory')

        if con.has_section(NcmirToolsConfig.DATASERVER_SECTION) is False:
            return None, ('No [' + NcmirToolsConfig.DATASERVER_SECTION +
                          '] section found in configuration. ')

        if con.has_option(NcmirToolsConfig.DATASERVER_SECTION,
                          NcmirToolsConfig.DATASERVER_DATADIR) is False:
            return None, ('No ' + NcmirToolsConfig.DATASERVER_DATADIR +
                          ' option found in configuration. ')

        searchdir = con.get(NcmirToolsConfig.DATASERVER_SECTION,
                            NcmirToolsConfig.DATASERVER_DATADIR)

        if con.has_option(NcmirToolsConfig.DATASERVER_SECTION,
                          NcmirToolsConfig.DATASERVER_IMGSUFFIX) is False:
            suffix = None
        else:
            suffix = con.get(NcmirToolsConfig.DATASERVER_SECTION,
                             NcmirToolsConfig.DATASERVER_IMGSUFFIX)

        if con.has_option(NcmirToolsConfig.DATASERVER_SECTION,
                          NcmirToolsConfig.DATASERVER_DIRSTOEXCLUDE) is False:
            d_to_exclude_list = None
        else:
            d_exclude = con.get(NcmirToolsConfig.DATASERVER_SECTION,
                                NcmirToolsConfig.DATASERVER_DIRSTOEXCLUDE)
            d_to_exclude_list = d_exclude.split(',')

        secondyoungests = SecondYoungest(searchdir, suffix,
                                         d_to_exclude_list)
        return secondyoungests, None
