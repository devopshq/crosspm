#!/usr/bin/env python
# -*- coding: utf-8 -*-
from crosspm import CrossPM
# argv = 'download -c "Z:\\home\\positive\\crosspm\\test\\test6\\crosspm.yaml" ' \
#        '--depslock-path="Z:\\home\\positive\\crosspm\\test\\test6\\dependencies.txt" ' \
#        '--out-format=shell ' \
#        '--output=found.sh'
# argv = 'download -c "Z:\\home\\positive\\crosspm\\test\\test6\\crosspm.yaml" --depslock-path="Z:\\home\\positive\\crosspm\\test\\test6\\dependencies.txt"'
argv = 'download -c "Z:\\home\\positive\\crosspm\\test\\test11\\config.yaml" --depslock-path="Z:\\home\\positive\\crosspm\\test\\test11\\dependencies.txt"'
# argv = 'download --depslock-path="Z:\\home\\positive\\crosspm\\test\\test6\\dependencies.txt"'
print(CrossPM(argv, return_result=True).run())
