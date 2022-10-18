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
    python_requires='>=3.6.0',
    classifiers=[
        'Development Status :: {}'.format(develop_status),
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
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
        "pytest>=5.2",
        "pytest-flask>=1.0.0",
        "PyYAML>=5.2",
    ],
    install_requires=[
        "requests>=2.25.1,<3.0.0",
        'urllib3<1.25,>=1.21.1',
        'docopt==0.6.2',
        "PyYAML>=5.2,<6.0",
        "dohq-artifactory>=0.8.3",
        "Jinja2>=2.11",
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
