#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from crosspm import config

setup(
    name='crosspm',
    version=config.__version__,
    description='Cross Package Manager',
    long_description=open('README.md').read(),
    license='MIT',
    author='Alexander Kovalev',
    author_email='ak@alkov.pro',
    url='http://devopshq.github.io/crosspm',
    download_url='https://github.com/devopshq/crosspm.git',
    entry_points={'console_scripts': ['crosspm=crosspm.__main__:main']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=[
        'development',
        'dependency',
        'requirements',
        'manager',
        'versioning',
        'packet',
    ],
    packages=[
        'crosspm',
        'crosspm.helpers',
        'crosspm.adapters',
    ],
    setup_requires=[
        'wheel',
    ],
    tests_require=[
        'pytest',
        'pytest-flask',
        'pyyaml',
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
            '../README.md',
        ],
    },
)
