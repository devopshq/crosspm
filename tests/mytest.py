import re

def split_with_regexp(regexp, text):
    prev_pos = 0
    _res = []
    for x in [[x.group()[1:-1].strip(), x.span()] for x in re.finditer(regexp, text)]:
        if x[1][0] > prev_pos:
            _res += [[text[prev_pos:x[1][0]], False]]
        _res += [[x[0], True]]
        prev_pos = x[1][1]
    if prev_pos < len(text) - 1:
        _res += [[text[prev_pos:], False]]
    return _res


val = "{int}.{int}.{int}[-{str}]"

must_not = split_with_regexp('\[.*?\]', val)

for i, x in enumerate(must_not):
    must_not[i] = [split_with_regexp('{.*?}', x[0]), x[1]]

for x in must_not:
    print(x)
