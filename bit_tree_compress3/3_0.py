# coding: utf-8
from collections import Counter
from pprint import pprint
import math


def recursive_func(ls):
    assert len(ls) >= 3
    ls.sort(key=lambda x: -x[0])

    pprint(ls)
    print()

    # выход из рекурсии
    if len(ls) == 3:
        return [
            ('0', ls[0][1]),
            ('1', ls[1][1]),
            ('2', ls[2][1]),
        ]

    ls2 = ls.copy()
    if len(ls2) - 2 > 3:
        # last 3 el
        p1, l1 = ls2.pop()
        p2, l2 = ls2.pop()
        p3, l3 = ls2.pop()
        ls2.append((p1+p2+p3, l1+l2+l3))
    else:
        p1, l1 = ls2.pop()
        p2, l2 = ls2.pop()
        ls2.append((p1+p2, l1+l2))
    result = recursive_func(ls2)  # уходим в рекурсию

    print('result:')
    pprint(result)
    print('ls:')
    pprint(ls)
    print()

    # result:
    # [('0', ['т', 'н', 'и', 'б', 'м', 'ч', 'я', 'у', 'а', ',', 'ь', 'ю', 'п', 'ж']),
    #  ('1', [' ', 'о']),
    #  ('2', ['й', 'г', 'л', 'р', 'к', 'д'])]
    # ls:
    # [(0.32432432432432434, [' ', 'о']),
    #  (0.24324324324324326, ['й', 'г', 'л', 'р', 'к', 'д']),
    #  (0.21621621621621623, ['а', ',', 'ь', 'ю', 'п', 'ж']),
    #  (0.21621621621621623, ['т', 'н', 'и', 'б', 'м', 'ч', 'я', 'у'])]

    result2 = []
    not_found = []
    while len(ls) > 0:
        _, l1 = ls.pop()
        is_found = False
        for v, l2 in result:
            if l1 == l2:
                result.remove((v, l1))
                result2.append((v, l1))
                is_found = True
                break
        if not is_found:
            not_found.append(('', l1))

    assert len(result) == 1
    pprint(result)
    pprint(result2)
    pprint(not_found)
    print()

    for i, (_, l) in enumerate(not_found):
        result2.append((result[0][0]+str(i), l))

    return result2     # обратный ход рекурсии


def main():
    ls = []
    text = '<skip>'
    for letter, count in Counter(text).most_common():
        ls.append((count, [letter]))

    print (len (ls))

    ls = recursive_func(ls)
    pprint(ls)

    d = {}
    for v, k in ls:
        print('%s - %s' % (v, k[0]))
        d[k[0]] = v

    for i in text:
        print(d[i], end='')


if __name__ == '__main__':
    main()
