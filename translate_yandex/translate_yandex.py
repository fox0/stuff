#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys
import logging
import requests
from gui import QApplication, MyWidget
from json_storage import JsonStorageGZ

DEBUG = True
#~ DEBUG = False

log = logging.getLogger(__name__)
cache_tr = {}


def func(text):
    result = []
    for line in text.split('\n'):
        line2 = re.sub(r'(\w+)', func_sub, line)
        result.append(line2)
    return '\n'.join(result)


def func_sub(m):
    word = m.group(1)
    r = yandex_tr(word)
    log.debug(r)
    if r:
        return r[0][0]
        # TODO (_, _)
        #~ s = (i[0] for i in r[1:])
        #~ return '%s/* (%s) %s */' % (r[0][0], word, ', '.join(s))
    return m.group(0)


def _cache(func):
    def decorator(word):
        try:
            result = cache_tr[word]
            log.debug('hit cache')
        except KeyError:
            # TODO cache_ignore
            result = func(word)
            cache_tr[word] = result
        return result
    return decorator


@_cache
def yandex_tr(word):
    log.debug(word)
    result = []
    url = 'http://dictionary.yandex.net/dicservice.json/lookup'
    r = requests.get(url, {
        # 'key': key_api,
        'text': word,
        'lang': 'en-ru',
    }).json()
    for i in r['def']:
        for j in i['tr']:
            result.append((j['text'], j['pos']))
    return result


def log_init():
    level_logging = logging.DEBUG if DEBUG else logging.INFO
    logging.basicConfig(
        format='%(levelname)s:%(name)s:%(funcName)s():%(lineno)d: %(message)s',
        level=level_logging
    )


if __name__ == '__main__':
    log_init()
    log.debug('load cache')
    db = JsonStorageGZ('cache')
    try:
        cache_tr = db.load()
    except FileNotFoundError:
        pass

    app = QApplication(sys.argv)
    w = MyWidget()
    w.setWindowTitle('tr')
    w.func = func
    w.show()
    res = app.exec_()

    log.debug('save cache')
    db.save(cache_tr)

    sys.exit(res)
