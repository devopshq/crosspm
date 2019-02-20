Cross Package Manager (CrossPM)
=======

[![build](https://travis-ci.org/devopshq/crosspm.svg?branch=master)](https://travis-ci.org/devopshq/crosspm)
[![codacy](https://api.codacy.com/project/badge/Grade/7a9ed2e6bb3e445f9e4a776e9b7f7886)](https://www.codacy.com/app/devopshq/crosspm/dashboard)
[![pypi](https://img.shields.io/pypi/v/crosspm.svg)](https://pypi.python.org/pypi/crosspm)
[![license](https://img.shields.io/pypi/l/crosspm.svg)](https://github.com/devopshq/crosspm/blob/master/LICENSE)

<!--ts-->
   * [Cross Package Manager (CrossPM)](#cross-package-manager-crosspm)
      * [Introduction](#introduction)
      * [Installation](#installation)
      * [Usage](#usage)
      * [Other pages](#other-pages)
      * [Development](#development)
<!--te-->

Introduction
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

CrossPM uses Python 3.4-3.6

Installation
------------
To install CrossPM, simply:
```
  pip install crosspm
```

Usage
-----
To see commandline parameters help, run:
```
  crosspm --help
```

You'll see something like this:
```
Usage:
    crosspm download [options]
    crosspm lock [DEPS] [DEPSLOCK] [options]
    crosspm usedby [DEPS] [options]
    crosspm pack <OUT> <SOURCE> [options]
    crosspm cache [size | age | clear [hard]]
    crosspm -h | --help
    crosspm --version

Options:
    <OUT>                                Output file.
    <SOURCE>                             Source directory path.
    -h, --help                           Show this screen.
    --version                            Show version.
    -L, --list                           Do not load packages and its dependencies. Just show what's found.
    -v LEVEL, --verbose=LEVEL            Set output verbosity: ({verb_level}) [default: ].
    -l LOGFILE, --log=LOGFILE            File name for log output. Log level is '{log_default}' if set when verbose doesn't.
    -c FILE, --config=FILE               Path to configuration file.
    -o OPTIONS, --options OPTIONS        Extra options.
    --deps-path=FILE                     Path to file with dependencies [./{deps_default}]
    --depslock-path=FILE                 Path to file with locked dependencies [./{deps_lock_default}]
    --dependencies-content=CONTENT       Content for dependencies.txt file
    --dependencies-lock-content=CONTENT  Content for dependencies.txt.lock file
    --lock-on-success                    Save file with locked dependencies next to original one if download succeeds
    --out-format=TYPE                    Output data format. Available formats:({out_format}) [default: {out_format_default}]
    --output=FILE                        Output file name (required if --out_format is not stdout)
    --output-template=FILE               Template path, e.g. nuget.packages.config.j2 (required if --out_format=jinja)
    --no-fails                           Ignore fails config if possible.
    --recursive=VALUE                    Process all packages recursively to find and lock all dependencies
    --prefer-local                       Do not search package if exist in cache
    --stdout                             Print info and debug message to STDOUT, error to STDERR. Otherwise - all messages to STDERR
```

Other pages
--------
- [Usage (RU)](usage/USAGE)
    - [CrossPM in Python as module](usage/USAGE-PYTHON)
    - [CrossPM in Cmake](usage/USAGE-CMAKE)
    - [CrossPM used by (RU)](usage/USAGE-USEDBY)
- [CrossPM Config](config/CONFIG)
    - [Import (RU)](config/IMPORT)
    - [Environment variables (RU)](config/Environment-variables)
    - [cpmconfig - Centralized distribution of configuration files](cpmconfig)
- [Output - get information about downloaded packages (RU)](config/OUTPUT)
    - [Output - template (RU)](config/output-template)
- [FAQ (RU)](FAQ)
- [Changelog](https://github.com/devopshq/crosspm/blob/master/CHANGELOG.md)

Development
--------

We use modified script for generate Table of content: https://github.com/ekalinin/github-markdown-toc
```bash
# Prepare
export GH_TOC_TOKEN="$(pwd)/token.txt" # or other path to token.txt with your github token
BASE=$(pwd) # crosspm git folder

# Process one file, eg FAQ.md
cd ./docs/kA
$BASE/gh-md-toc --insert FILENAME.MD

# Process all files
bash toc.sh
```
