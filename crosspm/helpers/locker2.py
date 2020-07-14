# -*- coding: utf-8 -*-
import os

from crosspm.helpers.config import CROSSPM_DEPENDENCY_FILENAME
from crosspm.helpers.content import DependenciesContent
from crosspm.helpers.downloader import Downloader
from crosspm.helpers.locker import Locker

from crosspm.helpers.parser2 import Parser2


class Locker2(Locker):
    def __init__(self, config, do_load, recursive):
        # TODO: revise logic to allow recursive search without downloading
        super(Locker2, self).__init__(config, do_load, recursive, Parser2)
