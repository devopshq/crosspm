from parse import compile

TAD_PARSER = compile('{}_{}_{}.deb')

class TadPackageNameParser:

    def __init__(self, package, version, arch):
        self.package = package
        self.version = version
        self.arch = arch

    @classmethod
    def parse_from_package_name(cls, package_name):
        package, version, arch = TAD_PARSER.parse(package_name)
        return TadPackageNameParser(package, version, arch)

    def __str__(self):
        return self.fullname

    def __repr__(self):
        return str(self)

    @property
    def fullname(self):
        return "{}_{}_{}.deb".format(self.package, self.version, self.arch)
