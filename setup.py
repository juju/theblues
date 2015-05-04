#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('CHANGELOG.rst').read().replace('.. :changelog:', '')

setup(
    name='theblues',
    version='0.0.3',
    description='Python library for using the juju charm store API.',
    long_description=readme + '\n\n' + history,
    author='JC Sackett',
    author_email='jcsackett@canonical.com',
    url='https://github.com/juju/theblues',
    packages=[
        'theblues',
    ],
    package_dir={'theblues': 'theblues'},
    include_package_data=True,
    install_requires=[
        'requests==2.6.0',
    ],
    tests_requires=[
        'httmock==1.2.3',
    ],
    zip_safe=False,
    keywords='theblues',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
)
