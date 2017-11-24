CrossPM
=======

[![build](https://travis-ci.org/devopshq/crosspm.svg?branch=master)](https://travis-ci.org/devopshq/crosspm)
[![codacy](https://api.codacy.com/project/badge/Grade/7a9ed2e6bb3e445f9e4a776e9b7f7886)](https://www.codacy.com/app/devopshq/crosspm/dashboard)
[![pypi](https://img.shields.io/pypi/v/crosspm.svg)](https://pypi.python.org/pypi/crosspm)
[![license](https://img.shields.io/pypi/l/crosspm.svg)](https://github.com/devopshq/crosspm/blob/master/LICENSE)

- [Documentation](#Chapter_2)
- [Installation](#Chapter_3)
- [Usage](#Chapter_4)
    - [Python](#Chapter_41)
- [Examples](#Chapter_5)
    - [crosspm.yaml](#Chapter_5_1)
    - [Config file description](#Chapter_5_2)
        - [import](#Chapter_5_2_1)
        - [cpm](#Chapter_5_2_2)
        - [cache](#Chapter_5_2_3)
        - [columns](#Chapter_5_2_4)
        - [values](#Chapter_5_2_5)
        - [options](#Chapter_5_2_6)
        - [parsers](#Chapter_5_2_7)
        - [defaults](#Chapter_5_2_8)
        - [solid](#Chapter_5_2_9)
        - [fails](#Chapter_5_2_10)
        - [common](#Chapter_5_2_11)
        - [sources](#Chapter_5_2_12)
        - [output](#Chapter_5_2_13)
        
<a name="Chapter_1"></a>Introduction
------------

CrossPM (Cross Package Manager) is a universal extensible package manager.
It lets you download and as a next step - manage packages of different types from different repositories.

Out-of-the-box modules:

- Adapters
  - Artifactory
  - [Artifactory-AQL](https://www.jfrog.com/confluence/display/RTF/Artifactory+Query+Language) (supported since artifactory 3.5.0):
  - files (simple repository on your local filesystem)

- Package file formats
  - zip
  - tar.gz
  - nupkg (treats like simple zip archive for now)

Modules planned to implement:

- Adapters
  - git
  - smb
  - sftp/ftp

- Package file formats
  - nupkg (nupkg dependencies support)
  - 7z

We also need your feedback to let us know which repositories and package formats do you need,
so we could plan its implementation.

The biggest feature of CrossPM is flexibility. It is fully customizable, i.e. repository structure, package formats,
packages version templates, etc.

To handle all the power it have, you need to write configuration file (**crosspm.yaml**)
and manifest file with the list of packages you need to download.

Configuration file format is YAML, as you could see from its filename, so you free to use yaml hints and tricks,
as long, as main configuration parameters remains on their levels :)

<a name="Chapter_2"></a>Documentation
-------------
Actual version always here: http://devopshq.github.io/crosspm

