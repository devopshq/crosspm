CrossPM Config
=======

<!--ts-->
   * [CrossPM Config](#crosspm-config)
   * [import](#import)
   * [cpm](#cpm)
      * [cpm:dependencies and cpm:dependencies-lock](#cpmdependencies-and-cpmdependencies-lock)
      * [cpm:lock-on-success](#cpmlock-on-success)
      * [cpm: prefer-local](#cpm-prefer-local)
   * [cache](#cache)
      * [cache:storage](#cachestorage)
      * [cache:clear - NOT used](#cacheclear---not-used)
   * [columns](#columns)
   * [values](#values)
   * [options](#options)
   * [parsers](#parsers)
      * [parsers:path](#parserspath)
   * [defaults](#defaults)
   * [solid:ext](#solidext)
   * [fails:unique](#failsunique)
   * [common](#common)
   * [sources](#sources)
   * [output:tree](#outputtree)
   * [Full example](#full-example)

<!-- Added by: aburov, at: 2019-01-16T18:15+07:00 -->

<!--te-->

# import
If defined, imports yaml config parts from other files. Must be the first parameter in config file.

```yaml
import:
- cred.yaml
- template-config.yaml
```
Read more about [`import` hacks (RU)](OUTPUT)

# `cpm`
Main configuration such as manifest file name and cache path.

```yaml
cpm:
  # Short description of your configuration file
  description: Simple example configuration
  
  dependencies: dependencies.txt
  dependencies-lock: dependencies.txt.lock
  lock-on-success: true
  prefer-local: True 
```

## `cpm:dependencies` and `cpm:dependencies-lock`
- `cpm:dependencies` - manifest file name (not path - just filename)
- `cpm:dependencies-lock` - manifest with locked dependencies (without masks and conditions) file name (not path - just filename). 
Equals to "dependencies" if not set.


## `cpm:lock-on-success`
If set to `true` (or yes or 1) - dependencies lock file will be generated after successfull **download**. 
Lock file will be saved near original dependencies file. 

## `cpm: prefer-local`
Search in local cache before query repo. 
Work only with:
- FIXED package version, without mask
- FIXED extenstion
- download-mode only (in lock it does not work)
- only in artifactory-aql adapters

# `cache`
Parameters for cache handling

```yaml
cache:
  cmdline: cache
  env: CROSSPM_CACHE_ROOT
#  default:
#  path:
  storage:
    packed: '{package}/{branch}/{version}/{compiler}/{arch}/{osname}/{package}.{version}.tar.gz'
    unpacked: '{package}/{branch}/{version}/{compiler}/{arch}/{osname}'
```
Several way to set where crosspm stored files (archive and unpacked package)
- `cache:cmdline` - Command line option name with path to cache folder.
- `cache:env` - Environment variable name with path to cache folder. Used if command line option is not set
- `cache:default` - Default path to cache folder. Used if command line option and environment variable are not set
- `cache:path` - `cmdline`, `env` and `default` are ignored if `path` set.

## cache:storage
Local storage setting, how `crosspm` will be stored files:
- `storage:packed` - path to packed file
- `storage:unpacked` - path to unpacked file 

## `cache:clear` - NOT used

```yaml
cache:
  ...
  # Parameters for cleaning cache.
  clear:
    #  Delete files or folders older than "days".
    days: 10
    # Delete older files and folders if cache size is bigger than "size". Could be in b, Kb, Mb, Gb. Bytes (b) is a default.
    size: 300 mb
    # Call cache check and clear before download
    auto: true
```

# `columns`

```yaml
columns: "*package, version, branch"
```


Let's keep in mind that any value we use in path, properties and columns description, called `column` in CrossPM.

Manifest file columns definition. Asterisk here points to name column (column of manifest file with package name). CrossPM uses it for building list with unique packages (i.e. by package name)

# `values`
Lists or dicts of available values for some columns (if we need it).
```yaml
values:
  quality:
    1: banned
    2: snapshot
    3: integration
    4: stable
    5: release
```

# `options`
Here we can define commandline options and environment variable names from which we will get some of columns values. We can define default values for those columns here too. Each option must be configured with this parameters:
- `cmdline` - Command line option name with option's value
- `env` - Environment variable name with option's value. Used if command line option is not set
- `default` - Default option's value. Used if command line option and environment variable are not set

# `parsers`
Rules for parsing columns, paths, properties, etc.
```yaml
parsers:
  common:
    columns:
      version: "{int}.{int}.{int}[.{int}][-{str}]"
    sort:
      - version
      - '*'
    index: -1
    usedby:
      AQL:
        "@dd.{package}.version": "{version}"
        "@dd.{package}.operator": "="

      property-parser:
        "deb.name": "package"
        "deb.version": "version"
        "qaverdict": "qaverdict"

  artifactory:
    path: "{server}/{repo}/{package}/{branch}/{version}/{compiler|any}/{arch|any}/{osname}/{package}.{version}[.zip|.tar.gz|.nupkg]"
    properties: "some.org.quality = {quality}"
```
- `columns` - Dictionary with column name as a key and template as a value.
Means that version column contains three numeric parts divided by a dot, followed by numeric or string or numeric and string parts with dividers or nothing at all:
```yaml
version: "{int}.{int}.{int}[.{int}][-{str}]"
```
- `sort` - List of column names in sorting order. Used for sorting packages if more than one version found 
for defined parameters. Asterisk can be one of values of a list representing all columns not mentioned here.
- `index` - Used for picking one element from sorted list. It's just a list index as in python.
- `properties` - Extra properties. i.e. object properties in Artifactory.

## `parsers:path`
Path template for searching packages in repository. Here {} is column, [|] is variation. 

```yaml
path: "{server}/{repo}/{package}/{compiler|any}/{osname}/{package}.{version}[.zip|.tar.gz]
```
these paths will be searched:
    
```yaml
https://repo.some.org/artifactory/libs-release.snapshot/boost/gcc4/linux/boost.1.60.204.zip
https://repo.some.org/artifactory/libs-release.snapshot/boost/gcc4/linux/boost.1.60.204.tar.gz
https://repo.some.org/artifactory/libs-release.snapshot/boost/any/linux/boost.1.60.204.zip
https://repo.some.org/artifactory/libs-release.snapshot/boost/any/linux/boost.1.60.204.tar.gz
```

Для того, чтобы задать любой путь, можно использовать `*`. Это пригодится, когда вам нужно выкачать пакеты, в оригинале не обращающие внимания на пути (`nupkg`, `deb`)
```yaml
# deb
parsers:
  common:
    columns:
      version: '{int}.{int}.{int}[.{int}]'
  artifactory-deb:
    path: '{server}/{repo}/pool/*/{package}.{version}.deb'

# nupkg
parsers:
  common:
    columns:
      version: '{int}.{int}.{int}[.{int}][-{str}]'
  artifactory-nupkg:
    path: '{server}/{repo}/pool/*/{package}.{version}.nupkg'
```
    

# `defaults`
Default values for columns not defined in "options".
```yaml
defaults:
  branch: master
  quality: stable
  # default support python format, like this:
  otherparams: "{package}/{version}"
```

# `solid:ext`
Set of rules pointing to packages which doesn't need to be unpacked. File name extension (i.e. ".tgz", ".tar.gz", or more real example ".deb").
```yaml
solid:
  ext: *.deb
```

# `fails:unique`
Here we can define some rules for failing CrossPM jobs. `fails:unique` - List of columns for generating unique index.
```yaml
fails:
  unique:
  - package
  - version
```


# `common`
Common parameters for all or several of sources.

```yaml
common:
  server: https://repo.some.org/artifactory
  parser: artifactory
  type: jfrog-artifactory
  auth_type: simple
  auth:
  - username
  - password
```

# `sources`
Sources definition. Here we define parameters for repositories access.
- `type` - Source type. Available types list depends on existing adapter modules.
- `parser` - Available parsers defined in parsers.
- `server` - Root URL of repository server.
- `repo` - Subpath to specific part of repository on server.
- `auth_type` - Authorization type. For example "simple".
- `auth` - Authorization data. For "simple" here we define login and password.

```yaml
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
```

# `output:tree`
Report output format definition. `tree` - columns and widths for tree output, printed in the end of CrossPM job.
```yaml
output:
  tree:
  - package: 25
  - version: 0
```


# Full example
We'll add some more examples soon. Here is one of configuration file examples for now.

**crosspm.yaml**
```yaml
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
  # - download-mode only (in lock it does not work)
  # - only in artifactory-aql adapters
  prefer-local: True 
  
cache:
  cmdline: cache
  env: CROSSPM_CACHE_ROOT
  storage:
    packed: '{package}/{branch}/{version}/{compiler}/{arch}/{osname}/{package}.{version}.tar.gz'
    unpacked: '{package}/{branch}/{version}/{compiler}/{arch}/{osname}'

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
    usedby:
      AQL:
        "@dd.{package}.version": "{version}"
        "@dd.{package}.operator": "="

      property-parser:
        "deb.name": "package"
        "deb.version": "version"
        "qaverdict": "qaverdict"

  artifactory:
    path: "{server}/{repo}/{package}/{branch}/{version}/{compiler|any}/{arch|any}/{osname}/{package}.{version}[.zip|.tar.gz|.nupkg]"
    properties: "some.org.quality = {quality}"
    
defaults:
  branch: master
  quality: stable
  # default support python format, like this:
  otherparams: "{package}/{version}"

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
