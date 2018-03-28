===============================
ncmirtools
===============================

.. image:: https://img.shields.io/pypi/v/ncmirtools.svg
     :target: https://pypi.python.org/pypi/ncmirtools
     :alt: Pypi 
.. image:: https://pyup.io/repos/github/crbs/ncmirtools/shield.svg
     :target: https://pyup.io/repos/github/crbs/ncmirtools/
     :alt: Updates

.. image:: https://travis-ci.org/CRBS/ncmirtools.svg?branch=master
       :target: https://travis-ci.org/CRBS/ncmirtools

.. image:: https://coveralls.io/repos/github/CRBS/ncmirtools/badge.svg?branch=master
       :target: https://coveralls.io/github/CRBS/ncmirtools?branch=master

.. image:: https://www.quantifiedcode.com/api/v1/project/1de1625cc49e4488b0fbd719cbfa0901/badge.svg
       :target: https://www.quantifiedcode.com/app/project/1de1625cc49e4488b0fbd719cbfa0901
       :alt: Code issues

Set of commandline tools for interaction with data hosted internally at NCMIR_.

For more information please visit our wiki page: 

https://github.com/CRBS/ncmirtools/wiki


Tools
-----

* **mpidir.py** -- Given a Microscopy product id, this script finds the path on the filesystem

* **projectdir.py** -- Given a project id, this script finds the path on the filesystem

* **projectsearch.py** -- Allows caller to search database for projects

* **mpidinfo.py** -- Queries database and returns information on specific Microscopy Product

* **imagetokiosk.py** -- Transfers second youngest image file to remote server via scp

Dependencies
------------

* `argparse <https://pypi.python.org/pypi/argparse>`_

* `configparser <https://pypi.python.org/pypi/configparser>`_

* `pg8000 <https://pypi.python.org/pypi/pg8000>`_

* `ftpretty <https://pypi.python.org/pypi/ftpretty>`_

* `paramiko <https://pypi.python.org/pypi/paramiko>`_

Compatibility
-------------

* Should work on Python 2.7, 3.3, 3.4, & 3.5 on Linux distributions


Installation
------------

Try one of these:

::

  pip install ncmirtools

  python setup.py install


License
-------

See LICENSE.txt_


Bugs
-----

Please report them `here <https://github.com/CRBS/ncmirtools/issues>`_


Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _NCMIR: https://ncmir.ucsd.edu/
.. _LICENSE.txt: https://github.com/CRBS/ncmirtools/blob/master/LICENSE.txt
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

