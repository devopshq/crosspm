#!/usr/bin/env python
# -*- coding: utf-8 -*-
from crosspm import CrossPM

argv = 'download -c "Z:\\home\\crosspm\\test\\test6\\crosspm.yaml" --depslock-path="Z:\\home\\crosspm\\test\\test6\\dependencies.txt"'
app = CrossPM(argv)
app.run()
