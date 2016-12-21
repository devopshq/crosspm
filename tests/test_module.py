#!/usr/bin/env python
# -*- coding: utf-8 -*-
from crosspm import CrossPM
import sys

argv = 'download -c "Z:\\home\\positive\\crosspm\\test\\test14\\crosspm.yaml" --depslock-path="Z:\\home\\positive\\crosspm\\test\\test14\\dependencies.txt" --no-fails'
err, res = CrossPM(argv, return_result=True).run()
if err == 0:  # Если не возникло других ошибок
    sys.stderr.write("\nCheck for multiple versions:\n\n")
    versions = {}
    for item in res:
        ver = versions.get(item['package'], [])
        ver_number = str(item['version'])
        if ver_number not in ver:
            ver.append(ver_number)
        versions[item['package']] = ver
    success = True
    for item, ver in versions.items():
        if len(ver) > 1:
            sys.stderr.write("{}: {}\n".format(item, str(ver)))
            success = False
    if success:
        sys.stderr.write("\nAll Ok!\n")
else:
    sys.stderr.write("\n{}\n{}".format(err, res))
