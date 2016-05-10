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
    version='0.3.1',
    description='Python library for using the juju charm store API.',
    long_description=readme + '\n\n' + history,
    author='Juju GUI Developers',
    author_email='juju-gui@lists.ubuntu.com',
    url='https://github.com/juju/theblues',
    packages=[
        'theblues',
    ],
    package_dir={'theblues': 'theblues'},
    include_package_data=True,
    install_requires=[
        'requests>=2.1.1',
        'jujubundlelib>=0.4.1',
    ],
    tests_requires=[
        'httmock==1.2.3',
    ],
    zip_safe=False,
    keywords='theblues',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 ' +
        '(LGPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
)
