#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

try:
    import rstcheck
    found_errors = False

    readme_errors = list(rstcheck.check(readme))
    if len(readme_errors) > 0:
        sys.stderr.write('\nErrors in README.rst [(line #, error)]\n' +
                         str(readme_errors) + '\n')
        found_errors = True

    history_errors = list(rstcheck.check(history))
    if len(history_errors) > 0:
        sys.stderr.write('\nErrors in HISTORY.rst [(line #, error)]\n' +
                         str(history_errors) + '\n')

        found_errors = True

    if 'sdist' in sys.argv or 'bdist_wheel' in sys.argv:
        if found_errors is True:
            sys.stderr.write('\n\nEXITING due to errors encountered in'
                             ' History.rst or Readme.rst.\n\nSee errors above\n\n')
            sys.exit(1)

except Exception as e:
    sys.stderr.write('WARNING: rstcheck library found, '
                     'unable to validate README.rst or HISTORY.rst\n')


requirements = [
    "argparse",
    "configparser",
    "pg8000",
    "ftpretty",
    "paramiko",
    "requests"
]

test_requirements = [
    "argparse",
    "pg8000",
    "configparser",
    "ftpretty",
    "paramiko",
    "requests",
    "mock"
]

setup(
    name='ncmirtools',
    version='0.5.1',
    description="Set of commandline tools for NCMIR",
    long_description=readme + '\n\n' + history,
    author="Christopher Churas",
    author_email='churas.camera@gmail.com',
    url='https://github.com/CRBS/ncmirtools',
    packages=[
        'ncmirtools', 'ncmirtools.kiosk',
    ],
    package_dir={'ncmirtools':
                 'ncmirtools'},
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='ncmirtools',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    scripts = [ 'ncmirtools/mpidir.py',
                'ncmirtools/projectsearch.py',
                'ncmirtools/projectdir.py',
                'ncmirtools/mpidinfo.py',
                'ncmirtools/imagetokiosk.py',
                'ncmirtools/ncmirtool.py'
              ],
    test_suite='tests',
    tests_require=test_requirements
)
