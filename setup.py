#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

import crosspm

setup(
    name='crosspm',
    version=crosspm.__version__,
    description='Cross Package Manager',
    license='MIT',
    author='Iaroslav Akimov',
    author_email='iaroslavscript@gmail.com',
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
