# -*- coding: utf-8 -*-


import os
import logging
import re
import pg8000
import math
from textwrap import TextWrapper

from ncmirtools.config import NcmirToolsConfig

logger = logging.getLogger(__name__)


class DirectorySearchPathError(Exception):
    """Raised when there is an error parsing Directory Search path
    """
    pass


class InvalidMicroscopyProductIdError(Exception):
    """Raised when MicroscopyProductId pass in is invalid
    """
    pass


class InvalidProjectIdError(Exception):
    """Raised when Project Id passed in is invalid
    """
    pass


class DirectoryForId(object):
    """Given a microscopy product id or project id
       instances of this class
       find corresponding directory on the filesystem
    """
    VOLUME_ID = '<VOLUME_ID>'
    MP_ID = '<MP_ID>'
    PROJECT_ID = '<PROJECT_ID>'

    # TODO: Make path platform agnostic ie use os.path.join
    PROJECT_DIR = ('/ccdbprod/ccdbprod<VOLUME_ID>/home'
                   '/CCDB_DATA_USER.portal/CCDB_DATA_USER'
                   '/acquisition/project_<PROJECT_ID>'
                   '/microscopy_<MP_ID>')

    def __init__(self, search_path):
        """Constructor
        :param search_path: string define search path. This path should have
                            values of `VOLUME_ID`, `PROJECT_ID`, and `MP_ID`
                             in it with the values in that order.
         See `PROJECT_DIR` value for default value
        :raises DirectorySearchPathError: If search_path parameter is None or
         invalid
        """
        self._search_path = search_path
        self._volpath = None
        self._projpath = None
        self._mpidpath = None

        if self._search_path is None:
            raise DirectorySearchPathError('search_path passed into '
                                           'constructor cannot be None')

        splitpath = re.split('^(.*)' +
                             DirectoryForId.VOLUME_ID +
                             '(.*)' +
                             DirectoryForId.PROJECT_ID +
                             '(.*)' +
                             DirectoryForId.MP_ID,
                             self._search_path)

        if len(splitpath) < 4:
            raise DirectorySearchPathError('Invalid search_path passed into '
                                           'constructor : ' + search_path)
        logger.debug(splitpath)
        self._volpath = splitpath[1]
        # TODO: Make path regex platform agnostic
        self._projpath = re.sub('^/', '', splitpath[2])
        self._mpidpath = re.sub('^/', '', splitpath[3])
        logger.debug('volpath=' + self._volpath + ' projpath=' +
                     self._projpath + 'mpidpath=' + str(self._mpidpath))

    def get_directory_for_microscopy_product_id(self, mpid):
        """Gets directory for microscopy product id `mpid`
        :param mpid: microscopy product id ie 5269524
        :returns: List of directories that match `mpid`
        """
        if mpid is None:
            raise InvalidMicroscopyProductIdError('microscopy product id '
                                                  'cannot be None')

        basedir = os.path.dirname(self._volpath)
        dirprefix = os.path.basename(self._volpath)
        match_vol_dirs = self._get_matching_directories(basedir,
                                                        dirprefix)
        logger.debug('vol dir count ' + str(len(match_vol_dirs)))
        project_dir_count = 0
        mp_dir_count = 0
        final_matches = []
        for vol_dir in match_vol_dirs:
            raw_prj_dir = os.path.join(vol_dir, self._projpath)
            basedir = os.path.dirname(raw_prj_dir)
            dirprefix = os.path.basename(raw_prj_dir)
            match_prj_dirs = self._get_matching_directories(basedir,
                                                            dirprefix)
            project_dir_count += len(match_prj_dirs)

            for mp_dir in match_prj_dirs:
                raw_mp_dir = os.path.join(mp_dir, self._mpidpath)
                basedir = os.path.dirname(raw_mp_dir)
                dirprefix = os.path.basename(raw_mp_dir) + str(mpid)
                match_mp_dirs = self._get_matching_directories(basedir,
                                                               dirprefix,
                                                               exactmatch=True)
                mp_dir_count += len(match_mp_dirs)
                if len(match_mp_dirs) > 0:
                    final_matches.extend(match_mp_dirs)

        logger.debug('project dir count ' + str(project_dir_count))
        logger.debug('mp_dir count ' + str(mp_dir_count))

        return final_matches

    def get_directory_for_project_id(self, projectid):
        """Gets directory for projectid id `projectid`
        :param projectid: microscopy product id ie 2080
        :returns: List of directories that match `projectid`
        """
        if projectid is None:
            raise InvalidProjectIdError('project id cannot be None')

        basedir = os.path.dirname(self._volpath)
        dirprefix = os.path.basename(self._volpath)
        match_vol_dirs = self._get_matching_directories(basedir,
                                                        dirprefix)
        logger.debug('vol dir count ' + str(len(match_vol_dirs)))
        project_dir_count = 0
        final_matches = []
        for vol_dir in match_vol_dirs:
            raw_prj_dir = os.path.join(vol_dir, self._projpath)
            basedir = os.path.dirname(raw_prj_dir)
            dirprefix = os.path.basename(raw_prj_dir + str(projectid))
            match_prj_dirs = self._get_matching_directories(basedir,
                                                            dirprefix,
                                                            exactmatch=True)
            project_dir_count += len(match_prj_dirs)
            if len(match_prj_dirs) > 0:
                final_matches.extend(match_prj_dirs)

        logger.debug('project dir count ' + str(project_dir_count))

        return final_matches

    def _get_matching_directories(self, basedir, prefix,
                                  exactmatch=False):
        """Gets list of directories under `basedir` matching `prefix`
        :param basedir: full path to directory to look under (ie
                        /ccdbprod)
        :param prefix: Any directory immediately under `basedir` that
                       starts with content of `prefix` is considered a

        :param exactmatch: Normally a match is found if directory under
                           `basedir` starts withe `prefix`, but if this
                           is True then only directories that exactly match
                           `prefix` are added to list
        :returns: List of strings that are full paths to directories matching
                  prefix
        """
        matching_dirs = []
        if basedir is None:
            logger.warning('basedir is None')
            return matching_dirs

        if prefix is None:
            logger.warning('prefix dir is None')
            return matching_dirs

        if exactmatch is None:
            logger.warning('exactmatch was set to None, using False')
            exactmatch = False

        logger.debug("thedir=" + basedir + " theprefix=" + prefix +
                     " exactmatch=" + str(exactmatch))

        if not os.path.isdir(basedir):
            logger.warning(basedir + ' is not a directory')
            return matching_dirs

        try:
            for entry in os.listdir(basedir):
                if exactmatch is False:
                    if entry.startswith(prefix):
                        fpath = os.path.join(basedir, entry)
                        if os.path.isdir(fpath):
                            matching_dirs.append(fpath)
                else:
                    if entry == prefix:
                        fpath = os.path.join(basedir, entry)
                        if os.path.isdir(fpath):
                            matching_dirs.append(fpath)
        except OSError:
            logger.exception('Caught Exception')
        return matching_dirs


class Database(object):
    """Gets connection to database using config passed in
    """
    def __init__(self, config):
        """Constructor
        :param config: ConfigParser object with information to connect to
                       database.
        """
        self._config = config
        self._alt_conn = None

    def set_config(self, config):
        """Sets alternate config
        :param config: ConfigParser object with information to connect to
                       database.
        """
        self._config = config

    def set_alternate_connection(self, conn):
        """Sets alternate database connection
        :param conn: Alternate database connection
        """
        self._alt_conn = conn

    def get_connection(self):
        """Gets connection to database
        :returns: Connection to database as Connection object
        """
        if self._alt_conn is not None:
            logger.info("Using alternate database connection")
            return self._alt_conn

        userval = self._config.get(NcmirToolsConfig.POSTGRES_SECTION,
                                   NcmirToolsConfig.POSTGRES_USER)

        passval = self._config.get(NcmirToolsConfig.POSTGRES_SECTION,
                                   NcmirToolsConfig.POSTGRES_PASS)

        hostval = self._config.get(NcmirToolsConfig.POSTGRES_SECTION,
                                   NcmirToolsConfig.POSTGRES_HOST)

        portval = self._config.get(NcmirToolsConfig.POSTGRES_SECTION,
                                   NcmirToolsConfig.POSTGRES_PORT)

        dbval = self._config.get(NcmirToolsConfig.POSTGRES_SECTION,
                                 NcmirToolsConfig.POSTGRES_DB)
        logger.debug('Getting database connection to pg8000')
        conn = pg8000.connect(host=hostval, user=userval,
                              password=passval,
                              port=int(portval),
                              database=dbval)
        return conn


class ProjectSearchViaDatabase(object):
    """Searches for Projects via Database
    """

    def __init__(self, config):
        """Constructor
        :param config: ConfigParser object with information to connect to
                       database.
        """
        self._database = Database(config)

    def set_config(self, config):
        """Sets alternate config
        :param config: ConfigParser object with information to connect to
                       database.
        """
        self._database.set_config(config)

    def set_alternate_connection(self, conn):
        """Sets alternate database connection
        :param conn: Alternate database connection
        """
        self._database.set_alternate_connection(conn)

    def get_matching_projects(self, keyword):
        """Finds projects matching keyword
        :param keyword: Keyword to use to search for projects
        :returns: list of strings containing project id followed by project
                  name.  Ex: 20333    some project
        """
        conn = self._database.get_connection()
        cursor = conn.cursor()
        res = []
        try:
            if keyword is None:
                logger.debug('keyword is None getting all projects')
                cursor.execute("SELECT Project_id,project_name FROM Project")
            else:
                cursor.execute("SELECT Project_id,project_name FROM Project "
                               "WHERE project_name ILIKE '%%" + keyword +
                               "%%' OR "
                               " project_desc ILIKE '%%" + keyword + "%%'")
            for tuple in cursor.fetchall():
                res.append(str(tuple[0]) + '    ' + str(tuple[1]))
        finally:
            cursor.close()
            conn.commit()
            conn.close()

        return res


class MicroscopyProduct(object):
    """Represents a CIL/CCDB Microscopy Product
    """
    ID_KEYWORD = 'Id:'
    IMAGE_BASENAME_KEYWORD = 'Image Basename:'
    NOTES_KEYWORD = 'Notes:'
    INDENT = '   '
    MAX_WIDTH = 70

    def __init__(self, mpid=None, image_basename=None,
                 notes=None):
        """Constructor
        """
        self._mpid = mpid
        self._image_basename = image_basename
        self._notes = notes
        pass

    def get_mpid(self):
        """Gets id for microscopy product
        :returns: microscopy product id
        """
        return self._mpid

    def get_image_basename(self):
        """Gets image basename for microscopy product
        :returns: image basename
        """
        return self._image_basename

    def get_notes(self):
        """Gets notes for microscopy product
        :returns: microscopy product id
        """
        return self._notes

    def get_as_string(self):
        """Returns microscopy product as a string
        that can be displayed on the command line to the
        user. Format:

        Id: <ID>

        Image Basename:

            <image basename>

        Notes:

            <notes>

        :returns: string describing this Microscopy Product
        """
        wrap = TextWrapper(initial_indent=MicroscopyProduct.INDENT,
                           subsequent_indent=MicroscopyProduct.INDENT,
                           width=MicroscopyProduct.MAX_WIDTH)
        return ('\n' + MicroscopyProduct.ID_KEYWORD + ' ' +
                str(self.get_mpid()) + '\n\n' +
                MicroscopyProduct.IMAGE_BASENAME_KEYWORD + '\n\n' +
                wrap.fill(str(self.get_image_basename())) +
                '\n\n' +
                MicroscopyProduct.NOTES_KEYWORD + '\n\n' +
                wrap.fill(str(self.get_notes())) + '\n\n')


class MicroscopyProductLookupViaDatabase(object):
    """Searches for Projects via Database
    """
    MAX_MPID = int(math.pow(2, 31))

    def __init__(self, config):
        """Constructor
        :param config: ConfigParser object with information to connect to
                       database.
        """
        self._database = Database(config)

    def set_config(self, config):
        """Sets alternate config
        :param config: ConfigParser object with information to connect to
                       database.
        """
        self._database.set_config(config)

    def set_alternate_connection(self, conn):
        """Sets alternate database connection
        :param conn: Alternate database connection
        """
        self._database.set_alternate_connection(conn)

    def get_microscopyproduct_for_id(self, mpid):
        """Finds projects matching keyword
        :param mpid: microscopy product id which must be an int less
                     then 2^32
        :returns: `MicroscopyProduct` object if found or None if
                  not found or if there was an error with the query
        """
        if mpid is None:
            logger.error('Microscopy Product id is none')
            return None

        if type(mpid) is not int:
            logger.error('Invalid Microscopy Product Id, must be an integer')
            return None

        if mpid >= MicroscopyProductLookupViaDatabase.MAX_MPID:
            logger.error('Microscopy Product Id cannot be larger then '
                         '2^32-1')
            return None

        conn = None
        cursor = None
        try:
            conn = self._database.get_connection()
            cursor = conn.cursor()
            logger.debug('Querying for Microscopy Product with '
                         'mpid: ' + str(mpid))
            cursor.execute("SELECT image_basename,notes FROM "
                           "Microscopy_products "
                           "WHERE mpid='" + str(mpid) + "'")
            if cursor.rowcount <= 0:
                logger.info('No Microsopy '
                            'Product found for id ' +
                            str(id))
                return None
            if cursor.rowcount > 1:
                logger.warning('More then one entry matches'
                               'this MicroscopyProduct id' +
                               str(mpid))
            tuple = cursor.fetchone()
            mp = MicroscopyProduct(mpid=str(mpid),
                                   image_basename=str(tuple[0]),
                                   notes=str(tuple[1]))
            return mp
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.commit()
                conn.close()
