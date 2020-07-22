from parse import compile

DEBIAN_PACKAGENAME_PATTERN = compile('{}_{}_{}.deb')

# https://www.debian.org/doc/manuals/debian-faq/pkg-basics.en.html
# 7.3. Why are Debian package file names so long?
# The Debian binary package file names conform to the following convention:
# <foo>_<VersionNumber>-<DebianRevisionNumber>_<DebianArchitecture>.deb


class DebianPackageNameParser:

    def __init__(self, package, version, revision, arch):
        self.package = package
        self.version = version
        self.revision = revision
        self.arch = arch

    @classmethod
    def parse_from_package_name(cls, package_name):
        package, fullversion, arch = DEBIAN_PACKAGENAME_PATTERN.parse(package_name)
        version, sep, revision = fullversion.partition('-')
        return DebianPackageNameParser(package, version, revision, arch)

    def __str__(self):
        return self.fullname

    def __repr__(self):
        return str(self)

    @property
    def fullname(self):
        return "{}_{}_{}.deb".format(self.package, self.version, self.arch)
