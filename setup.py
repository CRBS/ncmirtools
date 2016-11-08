#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "argparse",
    "configparser",
    "pg8000"
]

test_requirements = [
    "argparse",
    "pg8000",
    "configparser",
    "mock"
]

setup(
    name='ncmirtools',
    version='0.2.0',
    description="Set of commandline tools for NCMIR",
    long_description=readme + '\n\n' + history,
    author="Christopher Churas",
    author_email='churas.camera@gmail.com',
    url='https://github.com/CRBS/ncmirtools',
    packages=[
        'ncmirtools',
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
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    scripts = [ 'ncmirtools/mpidir.py',
                'ncmirtools/projectsearch.py',
                'ncmirtools/projectdir.py'
              ],
    test_suite='tests',
    tests_require=test_requirements
)
