Usage as Python module
=======
### Usage
You can use CrossPM in python-code:
```python
from crosspm import CrossPM
config_name = 'myconfig.yaml'
dependencies = 'dependencies.txt.lock'
argv = 'download -c "{}" --depslock-path="{}" --no-fails'.format(config_name, dependencies)

# run download and get result
# crosspm_raw_packages - LIST of all downloaded packages (with duplicate)
err, crosspm_raw_packages = CrossPM(argv, return_result='raw').run()

crosspm_unique_packages = set(crosspm_raw_packages)

# crosspm_tree_packages - LIST of first-level packages, with child in package.packages variable
err, crosspm_tree_packages = CrossPM(argv, return_result='tree').run()
```

### Package
You can get some Package field, like this:

```python
package = crosspm_tree_packages[0]
# class Package have this public interface:
print('Package has this dependencies')
dependencies_package = package.packages # access to all child packages
print(len(dependencies_package))

name = package.name # Package name
packed = package.packed_path # Path to archive (tar.gz\zip\nupkg
unpacked = package.unpacked_path # Path to unpacked folder
dup = package.duplicated # The package has a duplicate package with different version
package.get_name_and_path() # LEGACY - access to "name, unpacked_path"
package.get_file_path('some.exe') # Path to unpacked file (inside package)
package.get_file("some.exe") # Like "get_file_path" or None if file not exist

# Get package params like arch, branch, compiler, osname, version, repo, etc
params = package.get_params()
""" Return dict, like this
NB: version is list
{
  "arch": "x86",
  "branch": "1.9-pm",
  "compiler": "vc120",
  "osname": "win",
  "package": "libiconv",
  "repo": "libs-cpp-release",
  "version": ["1", "9", "131", "feature"] 
}
"""

# Get version in string format
params = package.get_params(merged=True)
"""
NB: version is list
{
  "arch": "x86",
  "branch": "1.9-pm",
  "compiler": "vc120",
  "osname": "win",
  "package": "libiconv",
  "repo": "libs-cpp-release",
  "version": "1.9.131-feature",
}
"""

# Get version in string format
params = package.get_params(param_list='version', merged=True)
"""
NB: version is list
{
  "version": "1.9.131-feature",
}
"""
params = package.get_params(param_list=['arch','version'], merged=True)
"""
NB: version is list
{
  "arch": "x86",
  "version": "1.9.131-feature",
}
"""
    
```