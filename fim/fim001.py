# coding: utf-8
import sys
from scaner import Scaner


DEBUG = True

scaner = None
res = []


def main(filename='test.fim'):
    with open(filename) as f:
        global res
        global scaner
        scaner = Scaner(f.read())
        token, value = scaner.pop()
        A_S(res).run()
        res_str = '\n'.join(res)
        print(res_str)
        code_obj = compile(res_str, '<string>', 'exec')
        exec(code_obj)


def a_print(value):
    debug()
    global res
    res.append('print(%s)' % a_vyr())


def a_vyr():
    token1, value1 = scaner.pop()
    token2, value2 = scaner.pop()
    token3, value3 = scaner.pop()
    return '%s%s%s' % (value1, token2, value3)


def a_pass(value):
    pass


def a_end(value):
    debug()
    global res
    res.append("if 'main' in list(locals().keys()):")
    res.append("    main()")
    res.append("")
    res.append("sys.exit(0)")


def pop(dic):
    tokens = list(dic.keys())
    token, value = scaner.pop()
    _assert(tokens, token, value)
    return token, value


def _assert(tokens, token, value):
    assert type(tokens) is list
    if token not in tokens:
        error(tokens, token, value)


def error(tokens, token, value):
    res.append("# warning: Ожидался <%s>. Найдено: <%s> = %s" % ('> или <'.join(tokens), token, value))
    # sys.exit(1)


def debug(mess=''):
    if DEBUG:
        res.append('# debug: %s(): %s' % (traceback.extract_stack()[-2][2], mess))


class A_S(object):
    """
    <start> ...
    """
    begin = {
        'print': a_print,
        'end': a_end,
    }

    def __init__(self, res):
        self.res = res

    def run(self):
        self.res.append("# coding: utf-8")
        self.res.append("import sys")
        self.res.append("")
        self.res.append("")
        while scaner.get():
            token, value = pop(self.begin)
            (self.begin[token] if token in self.begin else a_pass)(value)


if __name__ == '__main__':
    if DEBUG:
        import traceback
    # filename = sys.argv[1] if len(sys.argv) == 2 else
    main()
