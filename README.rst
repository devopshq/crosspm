CrossPM
=======

.. image:: https://travis-ci.org/devopshq/crosspm.svg?branch=master
    :target: https://travis-ci.org/devopshq/crosspm
.. image:: https://readthedocs.org/projects/crosspm/badge/?version=latest
    :target: https://crosspm.readthedocs.io/en/latest/?badge=latest
.. image:: https://img.shields.io/pypi/v/crosspm.svg
    :target: https://pypi.python.org/pypi/crosspm
.. image:: https://img.shields.io/pypi/l/crosspm.svg
    :target: https://pypi.python.org/pypi/crosspm

Introduction
------------

CrossPM (Cross Package Manager) is a universal extensible package manager.
It lets you download and as a next step - manage packages of different types from different repositories.

Out-of-the-box modules:

- Adapters

  - Artifactory

..

- Package file formats

  - zip
  - tar.gz
  - nupkg (treats like simple zip archive for now)

..

Modules planned to implement:

- Adapters

  - filesystem
  - git
  - smb
  - sftp/ftp

..

- Package file formats

  - nupkg (nupkg dependencies support)
  - 7z

..

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

We just started to write documentation for this project, but we'll try to cover all usage topics ASAP.

Here is direct link to it: https://crosspm.readthedocs.io


Installation
------------
To install CrossPM, simply::

  pip install crosspm


Usage
-----
To see commandline parameters help, run::

  crosspm --help

You'll see something like this::

  CrossPM (Cross Package Manager) version: *** The MIT License (MIT)

  Usage:
      crosspm download [options]
      crosspm promote [options]       * Temporarily off
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
      -v LEVEL, --verbose=LEVEL       Set output verbosity: ({verb_level}) [default: ].
      -l LOGFILE, --log=LOGFILE       File name for log output. Log level is '{log_default}' if set when verbose doesn't.
      -c FILE, --config=FILE          Path to configuration file.
      -o OPTIONS, --options OPTIONS   Extra options.
      --depslock-path=FILE            Path to file with locked dependencies [./{deps_lock_default}]
      --out-format=TYPE               Output data format. Available formats:({out_format}) [default: {out_format_default}]
      --output=FILE                   Output file name (required if --out_format is not stdout)
      --out-prefix=PREFIX             Prefix for output variable name [default: ] (no prefix at all)
      --no-fails                      Ignore fails config if possible.

Full description for each parameter will be added here some day before NY 2017 :)

Examples
--------

We'll add some more examples soon. Here is one of configuration file examples for now:

**crosspm.yaml**

.. list-table::
   :widths: 10 110
   :header-rows: 0

   * - ::

           1
           2
           3
           4
           5
           6
           7
           8
           9
          10
          11
          12
          13
          14
          15
          16
          17
          18
          19
          20
          21
          22
          23
          24
          25
          26
          27
          28
          29
          30
          31
          32
          33
          34
          35
          36
          37
          38
          39
          40
          41
          42
          43
          44
          45
          46
          47
          48
          49
          50
          51
          52
          53
          54
          55
          56
          57
          58
          59
          60
          61
          62
          63
          64
          65
          66
          67
          68
          69
          70
          71
          72
          73
          74
          75
          76
          77
          78
          79
          80
          81
          82
          83
          84
          85
          86
          87
          88
          89
          90
          91
          92
          93
          94
          95
          96

     - ::

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

..

**Config file description:**

Let's keep in mind that any value we use in path, properties and columns description, called column in CrossPM.

.. list-table::
   :widths: 20 250
   :header-rows: 0

   * - *import*
     - If defined, imports yaml config parts from other files.
       Must be the first parameter in config file.
   * - *cpm*
     - Main configuration such as manifest file name and cache path.

       .. list-table::
          :widths: 30 130
          :header-rows: 0

          * - *description*
            - Short description of your configuration file.
          * - *dependencies*
            - Manifest file name (not path - just filename)
          * - *dependencies-lock*
            - Manifest with locked dependencies (without masks and conditions) file name (not path - just filename).
              Equals to *dependencies* if not set.
          * - *cache*
            - Path for CrossPM temporary files, downloaded package archives and unpacked packages.
              Ignored if cache folder is configured in top *cache* item.

   * - *cache*
     - Parameters for cache handling.

       .. list-table::
          :widths: 30 130
          :header-rows: 0

          * - *cmdline*
            - Command line option name with path to cache folder.
          * - *env*
            - Environment variable name with path to cache folder. Used if command line option is not set.
          * - *default*
            - Default path to cache folder. Used if command line option and environment variable are not set.
          * - *path*
            - Path to cache folder. *cmdline*, *env* and *default* are ignored if *path* set.
          * - *clear*
            - Parameters for cleaning cache.

              .. list-table::
                 :widths: 30 100
                 :header-rows: 0

                 * - *days*
                   - Delete files or folders older than *days*.
                 * - *size*
                   - Delete older files and folders if cache size is bigger than *size*.
                     Could be in *b*, *Kb*, *Mb*, *Gb*. Bytes (*b*) is a default.
                 * - *auto*
                   - Call cache check and clear before download.

   * - *columns*
     - Manifest file columns definition.
       Asterisk here points to name column (column of manifest file with package name).
       CrossPM uses it for building list with unique packages (i.e. by package name)
   * - *values*
     - Lists or dicts of available values for some columns (if we need it).
   * - *options*
     - Here we can define commandline options and environment variable names from which we will get some of columns values.
       We can define default values for those columns here too. Each option must be configured with this parameters:

       .. list-table::
          :widths: 30 130
          :header-rows: 0

          * - *cmdline*
            - Command line option name with option's value.
          * - *env*
            - Environment variable name with option's value. Used if command line option is not set.
          * - *default*
            - Default option's value. Used if command line option and environment variable are not set.

   * - *parsers*
     - Rules for parsing columns, paths, properties, etc.

       .. list-table::
          :widths: 30 130
          :header-rows: 0

          * - *columns*
            - Dictionary with column name as a key and template as a value.
              Example::

                version: "{int}.{int}.{int}[.{int}][-{str}]"

              means that version column contains three numeric parts divided by a dot,
              followed by numeric or string or numeric and string parts with dividers or nothing at all.
          * - *sort*
            - List of column names in sorting order. Used for sorting packages if more than one version found for defined parameters.
              Asterisk can be one of values of a list representing all columns not mentioned here.
          * - *index*
            - Used for picking one element from sorted list. It's just a list index as in python.
          * - *path*
            - Path template for searching packages in repository. Here **{}** is column, **[|]** is variation.
              Example::

                path: "{server}/{repo}/{package}/{compiler|any}/{osname}/{package}.{version}[.zip|.tar.gz]"

              these paths will be searched::

                https://repo.some.org/artifactory/libs-release.snapshot/boost/gcc4/linux/boost.1.60.204.zip
                https://repo.some.org/artifactory/libs-release.snapshot/boost/gcc4/linux/boost.1.60.204.tar.gz
                https://repo.some.org/artifactory/libs-release.snapshot/boost/any/linux/boost.1.60.204.zip
                https://repo.some.org/artifactory/libs-release.snapshot/boost/any/linux/boost.1.60.204.tar.gz

          * - *properties*
            - Extra properties. i.e. object properties in Artifactory

   * - *defaults*
     - Default values for columns not defined in *options*.
   * - *solid*
     - Set of rules pointing to packages which doesn't need to be unpacked.

       .. list-table::
          :widths: 30 130
          :header-rows: 0

          * - *ext*
            - File name extension (i.e. ".tgz", ".tar.gz", or more real example ".deb")
   * - *fails*
     - Here we can define some rules for failing CrossPM jobs.

       .. list-table::
          :widths: 30 130
          :header-rows: 0

          * - *unique*
            - List of columns for generating unique index.
   * - *common*
     - Common parameters for all or several of sources.
   * - *sources*
     - Sources definition. Here we define parameters for repositories access.

       .. list-table::
          :widths: 30 130
          :header-rows: 0

          * - *type*
            - Source type. Available types list depends on existing adapter modules.
          * - *parser*
            - Available parsers defined in *parsers*.
          * - *server*
            - Root URL of repository server.
          * - *repo*
            - Subpath to specific part of repository on server.
          * - *auth_type*
            - Authorization type. For example *simple*.
          * - *auth*
            - Authorization data. For *simple* here we define login and password.
   * - *output*
     - Report output format definition.

       .. list-table::
          :widths: 30 130
          :header-rows: 0

          * - *tree*
            - columns and widths for tree output, printed in the end of CrossPM job.
