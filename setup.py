#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup
from crosspm import config

build_number = os.getenv('TRAVIS_BUILD_NUMBER', '')
branch = os.getenv('TRAVIS_BRANCH', '')
travis = any((build_number, branch,))
version = config.__version__.split('.')
develop_status = '4 - Beta'
url = 'http://devopshq.github.io/crosspm'

if travis:
    version = version[0:3]
    if branch == 'master':
        develop_status = '5 - Production/Stable'
        version.append(build_number)
    else:
        version.append('{}{}'.format('dev' if branch == 'develop' else branch, build_number))
else:
    if len(version) < 4:
        version.append('local')

version = '.'.join(version)
if travis:
    with open('crosspm/config.py', 'w', encoding="utf-8") as f:
        f.write("__version__ = '{}'".format(version))

with open('README.md', encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='crosspm',
    version=version,
    description='Cross Package Manager',
    license='MIT',
    author='Alexander Kovalev',
    author_email='ak@alkov.pro',
    url=url,
    long_description=long_description,
    download_url='https://github.com/devopshq/crosspm.git',
    entry_points={'console_scripts': ['crosspm=crosspm.__main__:main']},
    classifiers=[
        'Development Status :: {}'.format(develop_status),
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
        'crosspm.template',
    ],
    setup_requires=[
        'wheel',
        'pypandoc',
    ],
    tests_require=[
        'pytest',
        'pytest-flask',
        'pyyaml',
    ],
    install_requires=[
        'requests',
        'urllib3',
        'docopt',
        'pyyaml',
        'dohq-artifactory',
        'jinja2',
        'patool',  # need for pyunpack
        'pyunpack',
        # 'pyopenssl>=16.2.0',
        # 'cryptography>=1.7',
    ],
    package_data={
        '': [
            './template/*.j2',
            '*.cmake',
            '../LICENSE',
            # '../README.*',
        ],
    },
)
