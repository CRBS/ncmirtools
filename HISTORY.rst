=======
History
=======

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
