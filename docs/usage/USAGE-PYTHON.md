Usage as Python module
=======
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

package = crosspm_tree_packages[0]
# class Package have this public interface:
print('Package has this dependencies')
dependencies_package = package.packages # access to all child packages
print(len(dependencies_package))

print('Package name')
print(package.name)

print('Path to archive (tar.gz\zip\\nupkg)')
print(package.packed_path)

print('Path to unpacked folder')
print(package.unpacked_path)

print('The package has a duplicate package with different version')
print(package.duplicated)

print('LEGACY - access to "name, unpacked_path"')
print(package.get_name_and_path())

print('Path to unpacked file (inside package)')
print(package.get_file_path('some.exe'))

print('Like "get_file_path" or None if file not exist')
print(package.get_file("some.exe"))
```
