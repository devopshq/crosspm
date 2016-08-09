#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

import crosspm

setup(
    name='cpm',
    version=crosspm.__version__,
    description='Cross Package Manager',
    license='MIT',
    author='Alexander Kovalev',
    author_email='akovalev@ptsecurity.com',
    url='https://github.com/devopshq/crosspm.git',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords=[
        'development',
        'dependency',
        'requirements',
    ],
    packages=[
        'crosspm',
        'crosspm.helpers',
    ],
    setup_requires=[
        'pytest-runner',
        'wheel',
    ],
    tests_require=[
        'pytest',
        'pytest-flask',
    ],
    install_requires=[
        'requests',
        'docopt',
    ],
    package_data={
        '': [
            '*.cmake',
            '../LICENSE',
        ],
    },
)
