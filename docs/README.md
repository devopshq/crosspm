Cross Package Manager (CrossPM)
=======

[![build](https://travis-ci.org/devopshq/crosspm.svg?branch=master)](https://travis-ci.org/devopshq/crosspm)
[![codacy](https://api.codacy.com/project/badge/Grade/7a9ed2e6bb3e445f9e4a776e9b7f7886)](https://www.codacy.com/app/devopshq/crosspm/dashboard)
[![pypi](https://img.shields.io/pypi/v/crosspm.svg)](https://pypi.python.org/pypi/crosspm)
[![license](https://img.shields.io/pypi/l/crosspm.svg)](https://github.com/devopshq/crosspm/blob/master/LICENSE)


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
  CrossPM (Cross Package Manager) version: *** The MIT License (MIT)

  Usage:
      crosspm download [options]
      crosspm lock [DEPS] [DEPSLOCK] [options]
      crosspm pack <OUT> <SOURCE> [options]
      crosspm cache [size | age | clear [hard]]
      crosspm -h | --help
      crosspm --version

  Options:
      <OUT>                           Output file.
      <SOURCE>                        Source directory path.
      -h, --help                      Show this screen.
      --version                       Show version.
      -L, --list                      Do not load packages and its dependencies. Just show what's found.
      -v LEVEL, --verbose=LEVEL       Set output verbosity: (critical, error, warning, info, debug) [default: ].
      -l LOGFILE, --log=LOGFILE       File name for log output. Log level is 'info' if set when verbose doesn't.
      -c FILE, --config=FILE          Path to configuration file.
      -o OPTIONS, --options OPTIONS   Extra options.
      --deps-path=FILE                Path to file with dependencies [./dependencies.txt]
      --depslock-path=FILE            Path to file with locked dependencies [./dependencies.txt.lock]
      --lock-on-success               Save file with locked dependencies next to original one if download succeeds
      --out-format=TYPE               Output data format. Available formats:(['stdout', 'cmd', 'python', 'shell', 'json']) [default: stdout]
      --output=FILE                   Output file name (required if --out_format is not stdout)
      --no-fails                      Ignore fails config if possible.
      --recursive                     Process all packages recursively to find and lock all dependencies
```

Other pages
--------
- [Usage (RU)](usage/USAGE)
    - [CrossPM in Python as module](usage/USAGE-PYTHON)
    - [CrossPM in Cmake](usage/USAGE-CMAKE)
- [About config yaml-file](config/CONFIG)
    - [Environment variables (RU)](config/Environment-variables)
- [FAQ (RU)](FAQ)
- [Changelog](https://github.com/devopshq/crosspm/blob/master/CHANGELOG.md)
