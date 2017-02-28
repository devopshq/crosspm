from crosspm.helpers.parser import Parser


class BaseParserTest:
    _parsers = {}

    def init_parser(self, parsers):
        if 'common' not in parsers:
            parsers['common'] = {}
        for k, v in parsers.items():
            if k not in self._parsers:
                v.update({_k: _v for _k, _v in parsers['common'].items() if _k not in v})
                self._parsers[k] = Parser(k, v, self)
            else:
                return False
                # code = CROSSPM_ERRORCODE_CONFIG_FORMAT_ERROR
                # msg = 'Config file contains multiple definitions of the same parser: [{}]'.format(k)
                # self._log.exception(msg)
                # raise CrosspmException(code, msg)
        if len(self._parsers) == 0:
            return False
            # code = CROSSPM_ERRORCODE_CONFIG_FORMAT_ERROR
            # msg = 'Config file does not contain parsers! Unable to process any further.'
            # self._log.exception(msg)
            # raise CrosspmException(code, msg)
        return True
