# -*- coding: utf-8 -*-
import sys

CROSSPM_ERRORCODES = (
    CROSSPM_ERRORCODE_SUCCESS,
    CROSSPM_ERRORCODE_UNKNOWN_ERROR,
    CROSSPM_ERRORCODE_WRONG_ARGS,
    CROSSPM_ERRORCODE_FILE_DEPS_NOT_FOUND,
    CROSSPM_ERRORCODE_WRONG_SYNTAX,
    CROSSPM_ERRORCODE_MULTIPLE_DEPS,
    CROSSPM_ERRORCODE_NO_FILES_TO_PACK,
    CROSSPM_ERRORCODE_SERVER_CONNECT_ERROR,
    CROSSPM_ERRORCODE_PACKAGE_NOT_FOUND,
    CROSSPM_ERRORCODE_PACKAGE_BRANCH_NOT_FOUND,
    CROSSPM_ERRORCODE_VERSION_PATTERN_NOT_MATCH,
    CROSSPM_ERRORCODE_UNKNOWN_OUT_TYPE,
    CROSSPM_ERRORCODE_FILE_IO,
    CROSSPM_ERRORCODE_CONFIG_NOT_FOUND,
    CROSSPM_ERRORCODE_CONFIG_IO_ERROR,
    CROSSPM_ERRORCODE_CONFIG_FORMAT_ERROR,
    CROSSPM_ERRORCODE_ADAPTER_ERROR,
    CROSSPM_ERRORCODE_UNKNOWN_ARCHIVE,
) = range(18)


# Workaround for async stuff (something weird happens with plain print)
def print_stdout(*args, **kwargs):
    # kwargs.update({'file': sys.stdout})
    # print(*args, **kwargs)
    prn_str = ''.join(*args)
    sys.stderr.write('{}\n'.format(prn_str))
    sys.stderr.flush()


class CrosspmException(Exception):
    def __init__(self, error_code, msg=''):
        super().__init__(msg)
        self.error_code = error_code
        self.msg = msg


class CrosspmExceptionWrongArgs(CrosspmException):
    def __init__(self, msg=''):
        super().__init__(CROSSPM_ERRORCODE_WRONG_ARGS, msg)
