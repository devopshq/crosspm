CrossPM
=======

[![build](https://travis-ci.org/devopshq/crosspm.svg?branch=master)](https://travis-ci.org/devopshq/crosspm)
[![codacy](https://api.codacy.com/project/badge/Grade/7a9ed2e6bb3e445f9e4a776e9b7f7886)](https://www.codacy.com/app/devopshq/crosspm/dashboard)
[![pypi](https://img.shields.io/pypi/v/crosspm.svg)](https://pypi.python.org/pypi/crosspm)
[![license](https://img.shields.io/pypi/l/crosspm.svg)](https://github.com/devopshq/crosspm/blob/master/LICENSE)

*Index:*
- [Introduction](#Chapter_1)
    - [Changelog](#Chapter_11)
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

<a name="Chapter_12"></a>Changelog
------------
[Changelog](CHANGELOG.md)

<a name="Chapter_2"></a>Documentation
-------------
Actual version always here: http://devopshq.github.io/crosspm


<a name="Chapter_3"></a>Installation
------------
To install CrossPM, simply:
```
  pip install crosspm
```


<a name="Chapter_4"></a>Usage
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

<a name="Chapter_41"></a>Python
You can use CrossPM in python-code. [Read more](docs/USAGE-PYTHON.md)

<a name="Chapter_5"></a>Examples
--------
We'll add some more examples soon. Here is one of configuration file examples for now.

<a name="Chapter_5_1"></a> **crosspm.yaml**
```
import:
- cred.yaml

cpm:
  description: Simple example configuration
  dependencies: dependencies.txt
  dependencies-lock: dependencies.txt.lock
  lock-on-success: true
  
  # search in local cache before query repo. 
  # Work only with:
  # - FIXED package version, without mask
  # - FIXED extenstion
  # - download-mode only (in lock it do not work)
  # - only in artifactory-aql adapters
  prefer-local: True 
  
cache:
  cmdline: cache
  env: CROSSPM_CACHE_ROOT
  default:
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

<a name="Chapter_5_2"></a>**Config file description**

Let's keep in mind that any value we use in path, properties and columns description, called column in CrossPM.

<a name="Chapter_5_2_1"></a>***import*** - If defined, imports yaml config parts from other files. Must be the first parameter in config file.

<a name="Chapter_5_2_2"></a>***cpm*** - Main configuration such as manifest file name and cache path.

<dl>
  <dd><i>description</i> - Short description of your configuration file.</dd>
  <dd><i>dependencies</i> - Manifest file name (not path - just filename)</dd>
  <dd><i>dependencies-lock</i> - Manifest with locked dependencies (without masks and conditions) file name 
                                 (not path - just filename). Equals to "dependencies" if not set.</dd>
  <dd><i>lock-on-success</i> - If set to true (or yes or 1) - dependencies lock file will be generated
                               after successfull <b>download</b>. Lock file will be saved near original dependencies
                               file. Same behaviour could be triggered with a command line flag --lock-on-success</dd>
  <dd><i>cache</i> - Path for CrossPM temporary files, downloaded package archives and unpacked packages. 
                     Ignored if cache folder is configured in top "cache" item.</dd>
</dl>

<a name="Chapter_5_2_3"></a>***cache*** - Parameters for cache handling

<dl>
  <dd><i>cmdline</i> - Command line option name with path to cache folder.</dd>
  <dd><i>env</i> - Environment variable name with path to cache folder. Used if command line option is not set.</dd>
  <dd><i>default</i> - Default path to cache folder. Used if command line option and environment variable are not set.</dd>
  <dd><i>path</i> - Path to cache folder. "cmdline", "env" and "default" are ignored if "path" set.</dd>
  <dd><i>clear</i> - Parameters for cleaning cache.
  <dl>
    <dd><i>days</i> - Delete files or folders older than "days".</dd>
    <dd><i>size</i> - Delete older files and folders if cache size is bigger than "size". 
                      Could be in b, Kb, Mb, Gb. Bytes (b) is a default.</dd>
    <dd><i>auto</i> - Call cache check and clear before download.</dd>
  </dl>
  </dd>
</dl>

<a name="Chapter_5_2_4"></a>***columns*** - Manifest file columns definition. Asterisk here points to name column (column of manifest file with package name). CrossPM uses it for building list with unique packages (i.e. by package name)

<a name="Chapter_5_2_5"></a>***values*** - Lists or dicts of available values for some columns (if we need it).

<a name="Chapter_5_2_6"></a>***options*** - Here we can define commandline options and environment variable names from which we will get some of columns values. We can define default values for those columns here too. Each option must be configured with this parameters:

<dl>
  <dd><i>cmdline</i> - Command line option name with option's value.</dd>
  <dd><i>env</i> - Environment variable name with option's value. Used if command line option is not set.</dd>
  <dd><i>default</i> - Default option's value. Used if command line option and environment variable are not set.</dd>
</dl>

<a name="Chapter_5_2_7"></a>***parsers*** - Rules for parsing columns, paths, properties, etc.
    
<dl>
  <dd><i>columns</i> - Dictionary with column name as a key and template as a value.
  <dl>   
  <dd>Example:
        
        version: "{int}.{int}.{int}[.{int}][-{str}]"
    
  </dd>
  <dd>  
    means that version column contains three numeric parts divided by a dot, followed by numeric or string 
    or numeric and string parts with dividers or nothing at all.
  </dd>
  </dl>
  </dd>
  <dd><i>sort</i> - List of column names in sorting order. Used for sorting packages if more than one version found 
    for defined parameters. Asterisk can be one of values of a list representing all columns not mentioned here.</dd>
  <dd><i>index</i> - Used for picking one element from sorted list. It's just a list index as in python.</dd>
  <dd><i>path</i> - Path template for searching packages in repository. Here {} is column, [|] is variation.
  <dl>
  <dd>Example:
    
        path: "{server}/{repo}/{package}/{compiler|any}/{osname}/{package}.{version}[.zip|.tar.gz]"
    
  </dd>
  <dd>these paths will be searched:
    
        https://repo.some.org/artifactory/libs-release.snapshot/boost/gcc4/linux/boost.1.60.204.zip
        https://repo.some.org/artifactory/libs-release.snapshot/boost/gcc4/linux/boost.1.60.204.tar.gz
        https://repo.some.org/artifactory/libs-release.snapshot/boost/any/linux/boost.1.60.204.zip
        https://repo.some.org/artifactory/libs-release.snapshot/boost/any/linux/boost.1.60.204.tar.gz
    
  </dd>
  </dl>
  </dd>
  <dd><i>properties</i> - Extra properties. i.e. object properties in Artifactory.</dd>
</dl>

<a name="Chapter_5_2_8"></a>***defaults*** - Default values for columns not defined in "options".

<a name="Chapter_5_2_9"></a>***solid*** - Set of rules pointing to packages which doesn't need to be unpacked.
    
<dl>
  <dd><i>ext</i> - File name extension (i.e. ".tgz", ".tar.gz", or more real example ".deb").</dd>
</dl>

<a name="Chapter_5_2_10"></a>***fails*** - Here we can define some rules for failing CrossPM jobs.

<dl>
  <dd><i>unique</i> - List of columns for generating unique index.</dd>
</dl>

<a name="Chapter_5_2_11"></a>***common*** - Common parameters for all or several of sources.

<a name="Chapter_5_2_12"></a>***sources*** - Sources definition. Here we define parameters for repositories access.

<dl>
  <dd><i>type</i> - Source type. Available types list depends on existing adapter modules.</dd>
  <dd><i>parser</i> - Available parsers defined in parsers.</dd>
  <dd><i>server</i> - Root URL of repository server.</dd>
  <dd><i>repo</i> - Subpath to specific part of repository on server.</dd>
  <dd><i>auth_type</i> - Authorization type. For example "simple".</dd>
  <dd><i>auth</i> - Authorization data. For "simple" here we define login and password.</dd>
</dl>

<a name="Chapter_5_2_13"></a>***output*** - Report output format definition.
    
<dl>
  <dd><i>tree - columns and widths for tree output, printed in the end of CrossPM job.</dd>
</dl>
