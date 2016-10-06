#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import crosspm

setup(
    name='crosspm',
    version=crosspm.__version__,
    description='Cross Package Manager',
    license='MIT',
    author='Alexander Kovalev',
    author_email='ak@alkov.pro',
    url='https://github.com/devopshq/crosspm.git',
    entry_points={'console_scripts': ['crosspm=crosspm.__main__:main']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
        'crosspm.adapters',
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
        'pyyaml',
        'dohq-art',
    ],
    package_data={
        '': [
            '*.cmake',
            '../LICENSE',
        ],
    },
)
