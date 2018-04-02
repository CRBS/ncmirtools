=======
History
=======

0.5.1 (2018-04-02)
------------------

* Set delimiter for uploads to / to deal with problem uploading
  files from windows machine. 
  `Issue #18 <https://github.com/CRBS/ncmirtools/issues/18>`_

0.5.0 (2018-03-28)
------------------

* Created prototype cilupload tool. 
  Accessible via ncmirtool.py cilupload 
  `Issue #17 <https://github.com/CRBS/ncmirtools/issues/17>`_

* Created ncmirtool.py to prototype a single command line 
  script entry point. 
  `Issue #13 <https://github.com/CRBS/ncmirtools/issues/13>`_

* Dropped support for Python 2.6

0.4.0 (2017-06-28)
------------------

* Added imagetokiosk.py which transfers second youngest image
  file to remote server via scp.
  `Issue #16 <https://github.com/CRBS/ncmirtools/issues/16>`_

* Fixed a couple minor issues so this tool will work on 
  Windows. 
  `Issue #14 <https://github.com/CRBS/ncmirtools/issues/14>`_

0.3.0 (2017-01-13)
------------------

* Added mpidinfo.py script to provide information about 
  Microscopy Product from database. `Issue #6 <https://github.com/CRBS/ncmirtools/issues/6>`_

* Fixed bug in mpidinfo.py where passing id greater then 2^31 -1
  resulted in uncaught ProgrammingException `Issue #9 <https://github.com/CRBS/ncmirtools/issues/9>`_

* Consolidated all _setup_logging() calls into one function in config.py.
  `Issue #8 <https://github.com/CRBS/ncmirtools/issues/8>`_

* Modified NcmirToolsConfig to look for configuration file in /etc/ncmirtools.conf
  as well as the users home directory `Issue #7 <https://github.com/CRBS/ncmirtools/issues/7>`_


0.2.0 (2016-11-8)
------------------

* Added projectdir.py script which finds directories for a given
  project id. Issue #3

* Added projectsearch.py script which given a string will search
  a postgres database for projects with that string in the name
  or description. 


0.1.1 (2016-10-14)
------------------

* Minor improvements to README.rst for better presentation on pypi

0.1.0 (2016-10-04)
------------------

* Initial release with single script mpidir.py
