def fill_rule_inner(_cols, _pars=None):
    global _params
    if _pars is None:
        _pars = {}
    for _col in _cols:
        for _val in _col[1]:
            _pars[_col[0]] = _val
            if len(_cols) > 1:
                fill_rule_inner(_cols[1:], _pars)
            else:
                print(_pars)
                _params += [str(_pars)]
        break

a=[['cl',['1','2','3']],
   ['qt',['11','22','33','44']],
   ['os',['111','222']]]
_params = []
fill_rule_inner(a)

a=[['cl',['1','2','3']],
   ['qt',['11','22','33','44']]]
_params = []
fill_rule_inner(a)
# for x in _params:
#     print(x)

a=[['cl',['1','2','3']]]
_params = []
fill_rule_inner(a)
# for x in _params:
#     print(x)
