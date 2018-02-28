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

try:
    import pypandoc

    print("Converting README...")
    long_description = pypandoc.convert('README.md', 'rst')
    if branch:
        long_description = long_description.replace('crosspm.svg?branch=master', 'crosspm.svg?branch={}'.format(branch))
    index_begin = long_description.find('\n*Index:*')
    index_end = long_description.find('\nIntroduction')
    examples = long_description.find("\nYou'll see something")
    links = min((long_description.find('\n.. |build'),
                 long_description.find('\n.. |codacy'),
                 long_description.find('\n.. |pypi'),
                 long_description.find('\n.. |license'),
                 ))
    if all((index_begin >= 0,
            index_end >= 0,
            examples >= 0,
            links >= 0,
            )):
        long_description = '{}{}More information here: {}\n{}'.format(
            long_description[:index_begin],
            long_description[index_end:examples + 1],
            url,
            long_description[links:].replace('\n', '').replace('.. |', '\n.. |'),
        )  # .replace('\r\n', '\n')

except (IOError, ImportError, OSError):
    print("Pandoc not found. Long_description conversion failure.")
    with open('README.md', encoding="utf-8") as f:
        long_description = f.read()
else:
    print("Saving README.rst...")
    try:
        if len(long_description) > 0:
            with open('README.rst', 'w', encoding="utf-8") as f:
                f.write(long_description)
            if travis:
                os.remove('README.md')
    except:
        print("  failed!")

setup(
    name='crosspm',
    version=version,
    description='Cross Package Manager',
    license='MIT',
    author='Alexander Kovalev',
    author_email='ak@alkov.pro',
    url=url,
    # long_description=long_description,
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
        'docopt',
        'pyyaml',
        'dohq-artifactory>=0.2.62',
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
