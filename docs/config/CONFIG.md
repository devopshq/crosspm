CrossPM Config
=======
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

**Config file description**

Let's keep in mind that any value we use in path, properties and columns description, called column in CrossPM.

***import*** - If defined, imports yaml config parts from other files. Must be the first parameter in config file.

***cpm*** - Main configuration such as manifest file name and cache path.

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
  <dd><i>prefer-local</i> -# search in local cache before query repo. </dd>
</dl>

***cache*** - Parameters for cache handling

<dl>
  <dd><i>cmdline</i> - Command line option name with path to cache folder.</dd>
  <dd><i>env</i> - Environment variable name with path to cache folder. Used if command line option is not set.</dd>
  <dd><i>default</i> - Default path to cache folder. Used if command line option and environment variable are not set.</dd>
  <dd><i>path</i> - Path to cache folder. "cmdline", "env" and "default" are ignored if "path" set.</dd>
  <dd><i>storage</i> - local storage setting
  <dl>
    <dd><i>packed</i> - Path to packed file</dd>
    <dd><i>unpacked</i> - Path to UNpacked directory</dd>
  </dl>
  </dd>
  <dd><i>clear</i> - Parameters for cleaning cache.
  <dl>
    <dd><i>days</i> - Delete files or folders older than "days".</dd>
    <dd><i>size</i> - Delete older files and folders if cache size is bigger than "size". 
                      Could be in b, Kb, Mb, Gb. Bytes (b) is a default.</dd>
    <dd><i>auto</i> - Call cache check and clear before download.</dd>
  </dl>
  </dd>
</dl>

***columns*** - Manifest file columns definition. Asterisk here points to name column (column of manifest file with package name). CrossPM uses it for building list with unique packages (i.e. by package name)

***values*** - Lists or dicts of available values for some columns (if we need it).

***options*** - Here we can define commandline options and environment variable names from which we will get some of columns values. We can define default values for those columns here too. Each option must be configured with this parameters:

<dl>
  <dd><i>cmdline</i> - Command line option name with option's value.</dd>
  <dd><i>env</i> - Environment variable name with option's value. Used if command line option is not set.</dd>
  <dd><i>default</i> - Default option's value. Used if command line option and environment variable are not set.</dd>
</dl>

***parsers*** - Rules for parsing columns, paths, properties, etc.
    
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
  <dd>Example: <b>path: "{server}/{repo}/{package}/{compiler|any}/{osname}/{package}.{version}[.zip|.tar.gz]"</b>
    
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

***defaults*** - Default values for columns not defined in "options".

***solid*** - Set of rules pointing to packages which doesn't need to be unpacked.
    
<dl>
  <dd><i>ext</i> - File name extension (i.e. ".tgz", ".tar.gz", or more real example ".deb").</dd>
</dl>

***fails*** - Here we can define some rules for failing CrossPM jobs.

<dl>
  <dd><i>unique</i> - List of columns for generating unique index.</dd>
</dl>

***common*** - Common parameters for all or several of sources.

***sources*** - Sources definition. Here we define parameters for repositories access.

<dl>
  <dd><i>type</i> - Source type. Available types list depends on existing adapter modules.</dd>
  <dd><i>parser</i> - Available parsers defined in parsers.</dd>
  <dd><i>server</i> - Root URL of repository server.</dd>
  <dd><i>repo</i> - Subpath to specific part of repository on server.</dd>
  <dd><i>auth_type</i> - Authorization type. For example "simple".</dd>
  <dd><i>auth</i> - Authorization data. For "simple" here we define login and password.</dd>
</dl>

***output*** - Report output format definition.
    
<dl>
  <dd><i>tree - columns and widths for tree output, printed in the end of CrossPM job.</dd>
</dl>
