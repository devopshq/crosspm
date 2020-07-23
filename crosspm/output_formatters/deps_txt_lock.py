from tabulate import tabulate

class DepsTxtLockFormatter:
    def __init__(self):
        pass

    @staticmethod
    def write(lockfile_full_path, packages):

        packages_for_table = [[p.art_package.name, p.art_package.version] for p in packages.values()]
        table = tabulate(packages_for_table, headers=[], tablefmt='plain')

        with open(lockfile_full_path, 'w+') as f:
            f.write(table)
