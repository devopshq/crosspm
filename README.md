CrossPM
=======

[![crosspm build status](https://travis-ci.org/devopshq/crosspm.svg?branch=master)](https://travis-ci.org/devopshq/crosspm) [![crosspm code quality](https://api.codacy.com/project/badge/Grade/1b610f6ba99443908f914de0880ed6cc)](https://www.codacy.com/app/tim55667757/crosspm/dashboard) [![crosspm on PyPI](https://img.shields.io/pypi/v/crosspm.svg)](https://pypi.python.org/pypi/crosspm) [![FuzzyClassificator license](https://img.shields.io/pypi/l/crosspm.svg)](https://github.com/devopshq/crosspm/blob/master/LICENSE)

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


Documentation
-------------
Actual version always here: http://devopshq.github.io/crosspm


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
      --deps-path=FILE                Path to file with locked dependencies [./dependencies.txt]
      --depslock-path=FILE            Path to file with locked dependencies [./dependencies.txt]
      --out-format=TYPE               Output data format. Available formats:(['stdout', 'cmd', 'python', 'shell', 'json']) [default: stdout]
      --output=FILE                   Output file name (required if --out_format is not stdout)
      --no-fails                      Ignore fails config if possible.
```


Examples
--------
We'll add some more examples soon. Here is one of configuration file examples for now.

**crosspm.yaml**
```
import:
- cred.yaml

cpm:
description: Simple example configuration
dependencies: dependencies.txt
dependencies-lock: dependencies.txt.lock
cache:
  cmdline: cache
  env: CROSSPM_CACHE_ROOT
  default:

cache:
clear:
  days: 10
  size: 300 mb
  auto: true

columns: "*package, version, branch"

values:
quality:
  1: banned
  2: snapshot
  3: integration
  4: stable
  5: release

options:
compiler:
  cmdline: cl
  env: CROSSPM_COMPILER
  default: vc110

arch:
  cmdline: arch
  env: CROSSPM_ARCH
  default: x86

osname:
  cmdline: os
  env: CROSSPM_OS
  default: win

parsers:
common:
  columns:
    version: "{int}.{int}.{int}[.{int}][-{str}]"
  sort:
    - version
    - '*'
  index: -1

artifactory:
  path: "{server}/{repo}/{package}/{branch}/{version}/{compiler|any}/{arch|any}/{osname}/{package}.{version}[.zip|.tar.gz|.nupkg]"
  properties: "some.org.quality = {quality}"

defaults:
branch: master
quality: stable

solid:
ext: *.deb

fails:
unique:
  - package
  - version

common:
server: https://repo.some.org/artifactory
parser: artifactory
type: jfrog-artifactory
auth_type: simple
auth:
  - username
  - password

sources:
- repo:
    - libs-release.snapshot
    - libs-release/extlibs

- type: jfrog-artifactory
  parser: artifactory
  server: https://repo.some.org/artifactory
  repo: project.snapshot/temp-packages
  auth_type: simple
  auth:
    - username2
    - password2

output:
tree:
  - package: 25
  - version: 0
```

**Config file description**

Let's keep in mind that any value we use in path, properties and columns description, called column in CrossPM.

*import*
-- If defined, imports yaml config parts from other files. Must be the first parameter in config file.

*cpm*
-- Main configuration such as manifest file name and cache path.
    *description* -- Short description of your configuration file.
    *dependencies* -- Manifest file name (not path - just filename)
    *dependencies-lock* -- Manifest with locked dependencies (without masks and conditions) file name (not path - just filename). Equals to *dependencies* if not set.
    *cache* -- Path for CrossPM temporary files, downloaded package archives and unpacked packages. Ignored if cache folder is configured in top *cache* item.

*cache*
-- Parameters for cache handling
    *cmdline* -- Command line option name with path to cache folder.
    *env* -- Environment variable name with path to cache folder. Used if command line option is not set.
    *default* -- Default path to cache folder. Used if command line option and environment variable are not set.
    *path* -- Path to cache folder. *cmdline*, *env* and *default* are ignored if *path* set.
    *clear* -- Parameters for cleaning cache.
        *days* -- Delete files or folders older than *days*.
        *size* -- Delete older files and folders if cache size is bigger than         *size*. Could be in *b*, *Kb*, *Mb*, *Gb*. Bytes (*b*) is a default.
        *auto* -- Call cache check and clear before download.

*columns*
-- Manifest file columns definition. Asterisk here points to name column (column of manifest file with package name). CrossPM uses it for building list with unique packages (i.e. by package name)

*values*
-- Lists or dicts of available values for some columns (if we need it).

*options*
-- Here we can define commandline options and environment variable names from which we will get some of columns values. We can define default values for those columns here too. Each option must be configured with this parameters:
    *cmdline* -- Command line option name with option's value.
    *env* -- Environment variable name with option's value. Used if command line option is not set.
    *default* -- Default option's value. Used if command line option and environment variable are not set.

*parsers*
-- Rules for parsing columns, paths, properties, etc.
    *columns* -- Dictionary with column name as a key and template as a value. Example:
    ```
    version: "{int}.{int}.{int}[.{int}][-{str}]"
    ```
    means that version column contains three numeric parts divided by a dot, followed by numeric or string or numeric and string parts with dividers or nothing at all.
    *sort* -- List of column names in sorting order. Used for sorting packages if more than one version found for defined parameters. Asterisk can be one of values of a list representing all columns not mentioned here.
    *index* -- Used for picking one element from sorted list. It's just a list index as in python.
    *path* -- Path template for searching packages in repository. Here **{}** is column, **[|]** is variation. Example:
    ```
    path: "{server}/{repo}/{package}/{compiler|any}/{osname}/{package}.{version}[.zip|.tar.gz]"
    ```
    these paths will be searched:
    ```
    https://repo.some.org/artifactory/libs-release.snapshot/boost/gcc4/linux/boost.1.60.204.zip
    https://repo.some.org/artifactory/libs-release.snapshot/boost/gcc4/linux/boost.1.60.204.tar.gz
    https://repo.some.org/artifactory/libs-release.snapshot/boost/any/linux/boost.1.60.204.zip
    https://repo.some.org/artifactory/libs-release.snapshot/boost/any/linux/boost.1.60.204.tar.gz
    ```
    *properties* -- Extra properties. i.e. object properties in Artifactory

*defaults*
-- Default values for columns not defined in *options*.

*solid*
-- Set of rules pointing to packages which doesn't need to be unpacked.
        *ext* -- File name extension (i.e. ".tgz", ".tar.gz", or more real example ".deb")

*fails* -- Here we can define some rules for failing CrossPM jobs.
    *unique* -- List of columns for generating unique index.

*common*
-- Common parameters for all or several of sources.

*sources*
-- Sources definition. Here we define parameters for repositories access.
    *type* -- Source type. Available types list depends on existing adapter modules.
    *parser* -- Available parsers defined in *parsers*.
    *server* -- Root URL of repository server.
    *repo* -- Subpath to specific part of repository on server.
    *auth_type* -- Authorization type. For example *simple*.
    *auth* -- Authorization data. For *simple* here we define login and password.

*output*
-- Report output format definition.
    *tree* -- columns and widths for tree output, printed in the end of CrossPM job.
