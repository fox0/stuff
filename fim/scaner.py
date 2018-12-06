# coding: utf-8
import re


TOKENS = [
    # (expr, name),
    (r'Дорогая принцесса Селестия,', 'start'),
    (r'Ваша верная ученица,', 'end'),
    (r'Всегда ваша верная ученица,', 'end'),
    (r'Ваша преданная ученица,', 'end'),
    (r'Всегда ваша преданная ученица,', 'end'),

    (r'сказать', 'print'),

    (r'плюс', '+'),

    (r'\(', '('),
    (r'\)', ')'),
    (r'\.', '.'),
    (r',', ','),

    (r'=', '='),
    (r'\+=', '+='),
    (r'-=', '-='),
    (r'<<=', '<<='),
    (r'>>=', '>>='),

    (r'\+\+', '++'),
    (r'--', '--'),

    (r'0', 'const_int'),
    (r'[1-9]\d*', 'const_int'),

    (r'def\b', 'def'),
    (r'do\b', 'do'),
    (r'if\b', 'if'),
    (r'while\b', 'while'),

    (r'[a-z|A-Z]\w*\b', 'id'),  # [a-z|A-Z] ???
    (r'[а-я|А-Я]\w*\b', 'id'),
    ]
TOKENS = [(re.compile(expr), name) for expr, name in TOKENS]  # компилим


class Scaner(object):
    def __init__(self, text):
        self.text = text  # .replace('\n', ';')
        
    def get(self):
        return self._get(delete=False)

    def pop(self):
        return self._get(delete=True)

    def _get(self, delete):
        self.text = re.sub(r'^\s*', '', self.text, 1)  # пробелы
        if not self.text:
            return None
        for expr, token in TOKENS:
            res = expr.match(self.text)
            if res:
                if delete:
                    self.text = expr.sub('', self.text, 1)  # replace
                return token, res.group(0)
        print('error: Неизвестный токен: %s' % self.text.split('\n')[0])
