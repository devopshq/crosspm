#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup

from crosspm import config

build_number = os.getenv('GITHUB_RUN_NUMBER', '0')
branch = os.getenv('GITHUB_REF_NAME', '')
is_gh_actions = os.getenv('CI') == 'true'
version = config.__version__.split('.')
develop_status = '4 - Beta'
url = 'http://devopshq.github.io/crosspm'

if is_gh_actions:
    version = version[0:3]
    if branch == 'master':
        develop_status = '5 - Production/Stable'
        version.append(build_number)
    else:
        version.append('{}{}'.format('dev' if branch == 'develop' else branch, build_number))
else:
    if len(version) < 4:
        version.append('dev0')

version = '.'.join(version)
if is_gh_actions:
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
        'wheel==0.34.2',
        'pypandoc==1.5',
    ],
    tests_require=[
        "pytest<=4.6.9; python_version < '3.5'",
        "pytest>=5.2; python_version >= '3.5'",
        "pytest-flask<1.0.0; python_version < '3.5'",
        "pytest-flask>=1.0.0; python_version >= '3.5'",
        "PyYAML<5.2; python_version < '3.5'",
        "PyYAML>=5.2; python_version >= '3.5'",
    ],
    install_requires=[
        "requests<2.22; python_version < '3.5'",
        "requests>=2.22; python_version >= '3.5'",
        'urllib3==1.24.3',
        'docopt==0.6.2',
        "PyYAML==5.1.2; python_version < '3.5'",
        "PyYAML>=5.2; python_version >= '3.5'",
        "dohq-artifactory==0.4.112; python_version < '3.5'",
        "dohq-artifactory>=0.7.377; python_version >= '3.5'",
        "Jinja2<2.11; python_version < '3.5'",
        "Jinja2>=2.11; python_version >= '3.5'",
        'patool==1.12',  # need for pyunpack
        'pyunpack==0.2',
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
