#!/usr/bin/env python
# -*- coding: utf-8 -*-
from crosspm.cpm import App
import sys

def main():
    app = App()
    app.run()


if __name__ == '__main__':
    main()


# # Deprecated entry points for backward compatibility
# def download():
#     print('Calling "pm_arti_download.py <args>" is DEPRECATED! Use "crosspm download <args>" instead!')
#     sys.argv.insert(1, 'download')
#     main()
#
# 
# # Deprecated entry points for backward compatibility
# def pack():
#     print('Calling "pm_pack.py <args>" is DEPRECATED! Use "crosspm pack <args>" instead!')
#     sys.argv.insert(1, 'pack')
#     main()
#
#
# # Deprecated entry points for backward compatibility
# def promote():
#     print('Calling "pm_promote_deps.py <args>" is DEPRECATED! Use "crosspm promote <args>" instead!')
#     sys.argv.insert(1, 'promote')
#     main()
