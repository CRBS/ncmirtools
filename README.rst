===============================
ncmirtools
===============================



.. image:: https://pyup.io/repos/github/CRBS/ncmirtools/shield.svg
     :target: https://pyup.io/repos/github/CRBS/ncmirtools/
     :alt: Updates

.. image:: https://travis-ci.org/CRBS/ncmirtools.svg?branch=master
       :target: https://travis-ci.org/CRBS/ncmirtools

.. image:: https://coveralls.io/repos/github/CRBS/ncmirtools/badge.svg?branch=master
       :target: https://coveralls.io/github/CRBS/ncmirtools?branch=master

Set of commandline tools simplify interaction with the NCMIR CCDB/CIL data repository



Features
--------

* **mpidir.py** -- Given a Microscopy product id, this script finds the path on the filesystem


Requirements
------------

* Python 2.6 or 2.7
* Argparse
* Tested on Linux distributions


To Build
--------

::

  git clone https://github.com/CRBS/ncmirtools.git
  cd ncmirtools
  # if make is available
  make test
  make dist

  # if make is NOT available
  # python setup.py test
  # python setup.py bdist_wheel

  pip install dist/ncmirtools-*-py2.py3-none-any.whl


License
-------

See LICENSE.txt

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

