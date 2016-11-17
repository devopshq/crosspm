#!/usr/bin/env python
# -*- coding: utf-8 -*-
from crosspm import CrossPM
argv = 'download -c "Z:\\home\\positive\\crosspm\\test\\test6\\crosspm.yaml" --depslock-path="Z:\\home\\positive\\crosspm\\test\\test6\\dependencies.txt"'
print(CrossPM(argv).run())
