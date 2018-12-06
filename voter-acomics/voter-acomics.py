# coding: utf-8
import os
import re
import sys
import time
import socket
import random
import logging
import queue
import threading

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

list_cid = # <skip>

q = queue.Queue()


def set_hook(threads):
    _old_excepthook = sys.excepthook

    def excepthook(exctype, value, traceback):
        if exctype == KeyboardInterrupt:
            print()
            # for t in threads:
            #     t.kill()
            sys.exit(0)
        _old_excepthook(exctype, value, traceback)

    sys.excepthook = excepthook


def proxies_list():
    t = requests.get('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt').text
    ls = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', t)
    return [{'http': i} for i in ls]


def main():
    ls = [{}, {'http': '11.11.11.1:3128'}]
    ls += proxies_list()

    num_worker_threads = 16

    threads = []
    for i in range(num_worker_threads):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    set_hook(threads)

    for cid in list_cid:
        for proxies in ls:
            q.put((cid, proxies))

    # block until all tasks are done
    q.join()

    # # stop workers
    # for i in range(num_worker_threads):
    #     q.put(None)
    # for t in threads:
    #     t.join()
    log.info('all ok')


def worker():
    is_sleep = False
    while True:
        item = q.get()
        if item is None:
            break
        if is_sleep:
            seconds = random.randrange(0, 30)
            log.info('sleep %d seconds...', seconds)
            time.sleep(seconds)
        is_sleep = False
        try:
            is_sleep = run(*item)
        except (ConnectionResetError,
                requests.exceptions.ConnectionError,
                requests.exceptions.TooManyRedirects,
                requests.exceptions.HTTPError,
                requests.exceptions.ReadTimeout) as e:
            log.error(e)
        except BaseException as e:
            log.exception('fatal')
        q.task_done()


class R(object):
    def __init__(self):
        self.s = requests.Session()
        self.referer = None

    def get(self, url, **kwargs):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Cache-Control': 'max-age=0',
        }
        if self.referer:
            headers['Referer'] = self.referer
        response = self.s.request('GET', url, headers=headers, **kwargs)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        self.referer = url
        return response


class S(object):
    # TODO выбросить класс нафиг
    def __init__(self, filename):
        self.filename = os.path.join(os.path.dirname(__file__), filename)

    def load(self):
        with open(self.filename, 'r') as f:
            d = {}
            for i in f.read().split('\n'):
                if i:
                    k, v = i.split(' ', 1)
                    d[k] = v
            return d

    def save(self, d):
        ls = ['{} {}\n'.format(k, v) for k, v in d.items()]
        ls.sort()
        with open(self.filename, 'w') as f:
            f.writelines(ls)


def run(cid, proxies):
    s = R()
    s.s.proxies = proxies
    s.get('http://top.a-comics.ru/voter.php?q=ZA&cid=%d&T=0&G=0' % cid)
    time.sleep(random.randrange(3, 10))
    url2 = 'http://top.a-comics.ru/voter.php?q=CAPCHA&cid=%d&G=0&T=0' % cid
    response = s.get(url2)
    soup = BeautifulSoup(response.text, 'lxml')
    el = soup.find(id='central')

    params = {}
    answers = []
    for t in el.find_all('input'):
        if t['type'] == 'hidden':
            params[t['name']] = t['value']
        elif t['type'] == 'button':
            v = re.findall(r"'(.*)'", t['onclick'])
            answers.append((v[0], t['value']))

    captcha_url = 'http://top.a-comics.ru/{}'.format(el.find('img')['src'])
    f = S('captcha.txt')
    d = f.load()
    try:
        name = d[captcha_url]
        pic = None
        for tok, v in answers:
            if name == v:
                pic = tok
                break
        assert pic
        params['pic'] = pic
        response = s.get('http://top.a-comics.ru/voter.php', params=params)
        return is_ok(response)
    except KeyError:
        random.shuffle(answers)
        for tok, v in answers:
            params['pic'] = tok
            s.referer = url2
            response = s.get('http://top.a-comics.ru/voter.php', params=params)
            if is_ok(response):
                d[captcha_url] = v
                f.save(d)
                return True
    return False


def is_ok(response):
    t = response.text
    if 'Ошибочный запрос' in t:
        # log.error('Ошибочный запрос')
        return False
    if 'уже голосовали сегодня' in t:
        log.warning('уже голосовали сегодня')
        return True
    if 'Спасибо за вашу поддержку' in t:
        log.warning('ok')
        return True
    log.error(t)
    return False


class Tor(object):
    def __init__(self, address=('127.0.0.1', 9051), verbose=True):
        self.__s = socket.socket()
        self.__s.connect(address)
        self.f = self.__s.makefile('rwb')
        self.log = sys.stdout.write if verbose else lambda x: None

    def __del__(self):
        self.__s.close()

    def cmd(self, request):
        assert isinstance(request, str)
        self.log('>%s\n' % request)
        self.f.write(bytes(request.encode('utf8')))
        self.f.write(b'\r\n')
        self.f.flush()
        response = self.f.readline().decode('utf8')
        self.log(response)
        if not response.startswith('250 '):
            raise Exception()

    def wait(self, code):
        while True:
            response = self.f.readline().decode('utf8')
            self.log(response)
            if response.startswith('%d ' % code):
                break


def main_tor():
    tor = Tor()
    tor.cmd('authenticate "pass"')
    tor.cmd('setevents signal')

    for _ in range(128):
        for cid in list_cid:
            run(cid, {'http': 'socks5://127.0.0.1:9050'})
        tor.cmd('signal newnym')
        tor.wait(650)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    main_tor()
    main()
