# coding: utf-8
from io import BytesIO
from token import *
from tokenize import tokenize, untokenize

__version__ = '0.1'
DEBUG = True


def main():
    import sys
    sys.ps1 = '> '
    sys.ps2 = '. '
    __import__('code').interact(banner='FiM++ %s Rus' % __version__, readfunc=readfunc, local=get_locals())


def get_locals():
    сказать = print
    return locals()


def readfunc(prompt):
    string = input(prompt)
    tokens = get_tokenize(string)

    # tok_type, token, start, end, line = t
    # print('tokens:', tokens)
    res = get_untokenize(tokens)
    if DEBUG:
        print('>>%s' % res)
    return res


def get_tokenize(string):
    return tokenize(BytesIO(string.encode('utf-8')).readline)


def get_untokenize(tokens):
    return untokenize(tokens).decode('utf-8')


if __name__ == '__main__':
    main()
