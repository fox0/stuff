#!/usr/bin/env python3
# -*- coding: utf-8 -*-
try:
    import _thread as thread
except ImportError:
    import thread  # py2

import os
import time
import random
import logging
from datetime import datetime, timedelta

from parse_conf import load_conf, load_conf_dict
from json_storage import JsonStorageZip
from api import APISession, BoorySearch, API_VK  # , API_E926


DEBUG = True
#~ DEBUG = False

log = logging.getLogger(__name__)

#~ is_run_main = False
is_run_main = True

proxies_boory = {'https': 'socks5://127.0.0.1:9050'}

groups = (
    # (group_id, pony)
    ('13<skip>', 'twilight_sparkle'),
)

ignore_tags = load_conf('boory/ignore.conf')
vip_tags = load_conf('boory/vip.conf')
translate = load_conf_dict('boory/translate.conf')

vip_tags = list(translate.get(i, i) for i in vip_tags)


def is_6():
    """Завтра выходной, и бот запускаться не будет"""
    now = datetime.now()
    return False
    #~ return now.isoweekday() == 6


def init_log():
    level_logging = logging.DEBUG if DEBUG else logging.INFO
    logging.basicConfig(
        #~ filename='bot.log',  # ?
        format='%(levelname)s:%(name)s:%(funcName)s():%(lineno)d: %(message)s',
        level=level_logging,
        #~ loggers=['__main__']
    )


def get_api():  # TODO move into config
    """Фабрика"""
    return API_VK(
        #~ proxies={'https': "https://127.0.0.1:3128"},
        access_token='<skip>')


def run_boory(q, db_boory, max_images=50):
    # Access to adding post denied: you can only add 50 posts a day
    log.info(q)
    log.debug('run_boory')

    db = JsonStorageZip(db_boory)
    try:
        files = db.load()#[:-50]
    except FileNotFoundError:
        # TODO chmod
        files = []

    cdn = APISession(proxies=proxies_boory)

    result = []
    for i in BoorySearch(proxies=proxies_boory, q=q, sf='score', sd='desc'):
        if i['id'] in files:
            continue
        log.info('%d of %d', len(result)+1, max_images)

        thumbs = i['representations']
        filename = 'boory/%s' % thumbs['full'].split('/')[-1]
        if not os.path.exists(filename):
            cdn.download_file(thumbs['large'], filename)  # new  ###################################################
            #~ curl('https:%s' % thumbs['large'], filename)  # download it

        description = '\n'.join([
            prepare_tags(i['tags']),            # автор + теги
            '',
            i['description'].replace('undefined', '').replace('[bq]', '').replace('[/bq]', '').replace('#', '')
        ])
        caption = '\n'.join([
            description,
            '',
            'Источник: %s' % i['source_url'] if i['source_url'] else '',
            #~ 'Копия: https:%s' % thumbs['full'],
        ])

        result.append({
            #~ 'uid': i['id'],
            'filename': filename,
            'caption': caption,
            'description': description,
            'url': i['source_url'],
        })
        files.append(i['id'])

        if len(result) >= max_images:
            break

    log.info('saved %d files', len(result))
    db.save(files)
    return result


rule_replace = (
    (' ', '_'),
    #~ ('-', '_'),
    ('.', ''),
    ("'", ''),

)


def func_map(tag):
    """Обрабатываем каждый тег"""
    # TODO r'(.*)'
    for old, new in rule_replace:
        tag = tag.replace(old, new)
    for i in ('spoiler:', 'oc:', 'comic:', 'my_little_pony:_', 'fallout_equestria:_'):
        if tag.startswith(i):
            tag = tag[len(i):]  # откусываем
            break
    return translate.get(tag, tag)


def prepare_tags(tags):
    tags = list(map(func_map, tags.split(', ')))

    ls = tags
    ls = filter(lambda x: x not in ignore_tags, ls)
    ls = filter(lambda x: x not in vip_tags, ls)
    ls = filter(lambda x: not x.startswith('artist'), ls)
    ls = filter(lambda x: len(x) > 1, ls)
    ls = list(set(ls))

    ls_vip = ['mlp'] + list(filter(lambda x: x in vip_tags, tags))

    artists = filter(lambda x: x.startswith('artist'), tags)
    artists = map(lambda x: x[len('artist:'):], artists)
    artists = list(artists)

    log.debug(ls)
    log.debug('len(ls)=%d len(vip)=%d', len(ls), len(ls_vip))

    if len(ls_vip) > 10:
        res_ls = ls_vip[:10]
        not_ls = ls_vip[10:] + ls
    else:
        random.shuffle(ls)
        res_ls = ls_vip + ls[:10-len(ls_vip)]
        not_ls = ls[10-len(ls_vip):]
    assert len(res_ls) <= 10

    result = ''
    if artists:
        result += 'Автор: %s\n' % ', '.join(artists)
    result += '#%s' % ' #'.join(res_ls)
    #~ result += ' %s' % ' '.join(not_ls)
    log.debug(result)
    return result


def curl(url, filename):
    log.info('url=%s', url)
    os.system('curl --socks5 127.0.0.1:9050 %s > %s' % (url, filename))


def run_vk(ls, group_id, delta_minutes=10):
    delta_minutes = min(delta_minutes, 59)
    #~ api = get_api()
    # TODO now = api.utils_unix...
    now = datetime.now()

    days = 2 if is_6() else 1
    return post_on_days(ls, group_id, now, delta_minutes, days)


def post_on_days(ls, group_id, now, delta_minutes, days):
    api = get_api()

    tomorrow = now + timedelta(days=1)

    counter = 0
    if days == 1:
        half = len(ls) // 2

        arr = ls[:half]
        begin = now + timedelta(minutes=delta_minutes)
        end = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 4, 0, 0)
        counter += post_datetime(api, group_id, arr, begin, end)     # сегодня

        arr = ls[half:]
        begin = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 4, delta_minutes, 0)
        end = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 19, 0, 0)  # 9, 50, 0)
        counter += post_datetime(api, group_id, arr, begin, end)     # завтра

    #~ elif days == 2:
        #~ third = len(ls) // 3
        #~ counter += post_datetime(api, group_id, ls[:third],
            #~ now + timedelta(minutes=delta_minutes),
            #~ datetime(tomorrow.year, tomorrow.month, tomorrow.day, 4, 0, 0))      # суббота
        #~ tomorrow2 = tomorrow + timedelta(days=1)
        #~ counter += post_datetime(api, group_id, ls[third:2*third],
            #~ datetime(tomorrow.year, tomorrow.month, tomorrow.day, 4, delta_minutes, 0),
            #~ datetime(tomorrow2.year, tomorrow2.month, tomorrow2.day, 4, 0, 0))   # воскресенье
        #~ counter += post_datetime(api, group_id, ls[2*third:],
            #~ datetime(tomorrow2.year, tomorrow2.month, tomorrow2.day, 4, delta_minutes, 0),
            #~ datetime(tomorrow2.year, tomorrow2.month, tomorrow2.day, 9, 50, 0))  # понедельник

    #~ elif days == 3:
        #~ third = len(ls) // 3
        #~ counter += post_datetime(api, group_id, ls[:third],
            #~ now + timedelta(minutes=delta_minutes),
            #~ datetime(tomorrow.year, tomorrow.month, tomorrow.day, 4, 0, 0))     # сегодня
        #~ tomorrow2 = tomorrow + timedelta(days=1)
        #~ counter += post_datetime(api, group_id, ls[third:2*third],
            #~ datetime(tomorrow.year, tomorrow.month, tomorrow.day, 4, delta_minutes, 0),
            #~ datetime(tomorrow2.year, tomorrow2.month, tomorrow2.day, 4, 0, 0))
        #~ tomorrow3 = tomorrow2 + timedelta(days=1)
        #~ counter += post_datetime(api, group_id, ls[2*third:],
            #~ datetime(tomorrow2.year, tomorrow2.month, tomorrow2.day, 4, delta_minutes, 0),
            #~ datetime(tomorrow3.year, tomorrow3.month, tomorrow3.day, 9, 50, 0))

    else:
        raise NotImplementedError
    return counter


#~ _global_lock = []
#~ max_request_per_sec = 2
#~
#~
#~ def lock():
    #~ global _global_lock
    #~ while len(_global_lock) >= max_request_per_sec:
        #~ time_sleep = 2.
        #~ log.info('wait %f...', time_sleep)
        #~ time.sleep(time_sleep)
        #~ now = time.time()
        #~ _global_lock = [i for i in _global_lock if i > now - 60]
        #~ log.info('>count lock = %d of %d', len(_global_lock), max_request_per_sec)
    #~ _global_lock.append(time.time())


def post_datetime(api, group_id, ls, begin_date, end_date):
    #assert isinstance(api, API_VK)
    # assert isinstance(group_id, )
    assert isinstance(ls, list)
    assert isinstance(begin_date, datetime)
    assert isinstance(end_date, datetime)

    log.info('%s - %s', begin_date, end_date)
    len_ls = len(ls)
    if len_ls == 0:
        return 0

    publish_date = begin_date.timestamp()
    diff = (end_date.timestamp() - publish_date) // len_ls
    assert diff > 0

    counter = 0
    for index, i in enumerate(ls):
        log.info('%s %d of %d', datetime.fromtimestamp(publish_date), index+1, len_ls)
        try:
            #~ lock()  # TODO!!!
            r = api.group_wall_post_photo(**{
                'group_id': group_id,
                'photo': i['filename'],
                'publish_date': publish_date,
                'url': i['url'],
                'caption': i['caption'],
                'message': i['description'],
            })
        except BaseException as e:
            log.exception('BaseException')
            #~ send_log('post', 'error %s: %s' % (type(e), e))
        else:
            counter += 1
        publish_date += diff
    return counter


def send_log(pony, message):
    m = '[%s] %s' % (pony, message)
    log.info(m)
    api = get_api()
    try:
        #~ lock()  # TODO!!!
        api.messages_send(user_id='15<skip>', message=m)
    except BaseException as e:
        log.exception('BaseException')


Q = (
    'safe',
    'height.gte:400',
    'score.gte:10',
    'first_seen_at.gt:%d days ago' % 3,  # (7 if is_6() else 3)
    '-animated',
    '-screencap',
    '-meta',
    '-gay',
    '-fat',
    '-inflation',
    '-vore',
    '-picture for breezies',
)


def runme_mlp(max_images=50):
    try:
        ls = run_boory(q=', '.join(Q), db_boory='boory/mlp', max_images=max_images)
        counter = run_vk(ls, group_id='13<skip>')
        send_log('main', '+%d of %d' % (counter, len(ls)))
    except BaseException as e:
        send_log('main', 'error %s: %s' % (type(e), e))
        #~ raise  # (!)


def runme_pony(max_images=50):
    # TODO  распараллелить
    delta_minutes = 11  # на всякий случай, кто знает сколько скрипт будет работать, чтобы не постить в прошлое
    delta = (60-delta_minutes) // len(groups)
    log.info('delta = %d' % delta)
    for group_id, pony in groups:
        try:
            log.info(pony)
            Q2 = list(Q)
            Q2.append(pony.replace('_', ' '))
            ls = run_boory(q=', '.join(Q2), db_boory='boory/%s'%pony, max_images=max_images)
            counter = run_vk(ls, group_id=group_id, delta_minutes=delta_minutes)
            delta_minutes += delta
            send_log(pony, '+%d of %d' % (counter, len(ls)))
        except BaseException as e:
            send_log(pony, 'error %s: %s' % (type(e), e))
            #~ raise


def runme_stats():
    result = []
    api = get_api()
    now = datetime.now()
    date_from = now - timedelta(days=7)
    date_to = now - timedelta(days=1)
    date_from = datetime.strftime(date_from, '%Y-%m-%d')
    date_to = datetime.strftime(date_to, '%Y-%m-%d')

    ls = [('13<skip>', 'main')]
    ls.extend(groups)
    for group_id, pony in ls:
        result_reach = []
        r = api.stats_get(group_id=group_id, date_from=date_from, date_to=date_to)
        for i in reversed(r):
            # print(i.keys())
            result_reach.append(i.get('reach'))
        result.append('[%s] Полный охват: %s' % (pony, ' '.join(map(str, result_reach))))
    send_log('log', '\n'.join(result))


def runme_drop():
    log.info('deleting files...')
    os.system('rm -f boory/*.png')
    os.system('rm -f boory/*.jpeg')
    os.system('rm -f boory/*.gif')


def create_group(pony):
    """Создать новую группу"""
    api = get_api()
    group_id = api.groups_create(title='<skip>%s/' % pony)['id']
    res = api.groups_edit(
        group_id=group_id,
        wall=2,  # ограниченная
        photos=0,
        video=0,
        )
    if res != 1:
        raise BaseException
    api.groups_edit(
        group_id=group_id,
        screen_name='safe_%s' % pony,  #?
        description='''%s<skip>''' % pony)
    api.groups_editPlace(group_id=group_id)
    # TODO +краткое имя
    log.info('group_id=%s', group_id)

#~
#~ def test_e():
    #~ api = API_E926(proxies={'https': "socks5://127.0.0.1:9050"})
    #~ r = api.search(tags='rating:safe -animated date:3_days_ago score:>=10 order:score')
    #~ print(r)


if __name__ == '__main__':
    init_log()

    #~ create_group('sunset_shimmer')
    #~ import sys
    #~ sys.exit()

    max_images = 75 if is_6() else 50
    if is_run_main:
        thread.start_new_thread(runme_stats, ())
        runme_mlp(max_images=max_images)  # main
    runme_pony(max_images=max_images)
    runme_drop()
    send_log('main', 'exit')
