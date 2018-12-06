# coding: utf-8
import time
import logging
from packages import requests


log = logging.getLogger(__name__)


class APISession(object):
    """Устанавливает соединение с одним хостом и делает по нему запросы"""
    def __init__(self, proxies={}):
        session = requests.Session()
        session.proxies = proxies
        self._session = session

    def get_json(self, url, **get_params):
        return self._get(url, data=get_params).json()

    def download_file(self, url, filename):
        if url.startswith('//'):
            url = 'https:%s' % url
        response = self._get(url, stream=True)
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    def _get(self, url, **kwargs):
        response = self._session.get(url, **kwargs)
        response.raise_for_status()
        return response


class APIBoory(APISession):
    def search(self, **kwargs):
        return self.get_json('https://derpibooru.org/search.json', **kwargs)['search']


class BoorySearch(object):
    def __init__(self, proxies={}, **kwargs):
        self.kwargs = kwargs
        self.api = APIBoory(proxies=proxies)

    def __iter__(self):
        page = 1
        kwargs = self.kwargs
        while True:
            log.info('page #%d', page)
            kwargs['page'] = page
            ls = self.api.search(**kwargs)
            for image in ls:
                yield image
            if len(ls) != 15:  # for anon
                raise StopIteration
            page += 1


class AbstractAPI(object):
    # устарело
    def __init__(self, proxies={}, **kwargs):
        self.proxies = proxies
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def get(self, url, **kwargs):
        log.debug('> %s\n%s', url, kwargs)
        log.debug(self.proxies)
        response = requests.get(url, kwargs, proxies=self.proxies)
        response.raise_for_status()
        return response.json()

    def post(self, url, **kwargs):
        log.debug('> %s\n%s', url, kwargs)
        response = requests.post(url, kwargs, proxies=self.proxies)
        response.raise_for_status()
        return response.json()

    def post_files(self, url, files):
        log.debug('> %s', url)
        response = requests.post(url, files=files, proxies=self.proxies)
        response.raise_for_status()
        return response.json()


#~ class AbstractAPI(object):
    #~ def __init__(self, **kwargs):
        #~ self.proxies = {}
        #~ self.cookies = {}
        #~ for k, v in kwargs.items():
            #~ self.__setattr__(k, v)

    #~ def get(self, url, **kwargs):
        #~ log.debug('> %s\n%s', url, kwargs)
        #~ log.debug(self.proxies)
        #~ response = requests.get(url, kwargs, proxies=self.proxies)
        #~ response.raise_for_status()
        #~ return response.json()

    #~ def post(self, url, **kwargs):
        #~ log.debug('> %s\n%s', url, kwargs)
        #~ response = requests.post(url, kwargs, proxies=self.proxies, cookies=self.cookies)
        #~ response.raise_for_status()
        #~ self.cookies.update(response.cookies)
        #~ return response.json()

    #~ def post_files(self, url, files):
        #~ log.debug('> %s', url)
        #~ response = requests.post(url, files=files, proxies=self.proxies)
        #~ response.raise_for_status()
        #~ return response.json()


class API_E926(AbstractAPI):
    def search(self, **kwargs):
        return self.get('https://e926.net/post/index.json', **kwargs)


class API_VK_Error(BaseException):
    def __init__(self, result):
        log.debug('%s', result)
        for k, v in result['error'].items():
            self.__setattr__(k, v)

    def __str__(self):
        return '[%s]: %s\n%s' % (self.error_code, self.error_msg, self.request_params)


class API_VK_Simple(AbstractAPI):
    VERSION_API = '5.60'

    def __getattr__(self, attr):
        # just add magic...
        url = 'https://api.vk.com/method/%s' % attr.replace('_', '.')

        def func(**kwargs):
            kwargs['v'] = self.VERSION_API
            kwargs['access_token'] = self.access_token
            for _ in range(3):
                result = self.post(url, **kwargs)
                try:
                    return result['response']
                except KeyError:
                    e = API_VK_Error(result)
                    if e.error_code == 10:  # Internal server error: Database problems, try later
                        log.error('oops...')
                        time.sleep(.5)
                    else:
                        raise e

        self.__setattr__(attr, func)
        return func


class API_VK(API_VK_Simple):
    def group_wall_post_photo(self, group_id, photo, caption=None, url=None, **kwargs):
        """Опубликовать фотографию на стене группы"""
        p = self.upload_photo_for_wall(group_id, photo, caption)
        d = {
            'owner_id': '-%s' % (group_id,),
            'from_group': '1',
            'attachments': p,
        }
        if url:
            d['attachments'] += ',%s' % url

        for key in ['message', 'publish_date', 'uid']:
            try:
                d[key] = kwargs[key]
            except KeyError:  # ???
                pass
        return self.wall_post(**d)

    def upload_photo_for_wall(self, owner_id, filename, caption=None):
        """Загрузить фотографию для стены"""
        r1 = self.photos_getWallUploadServer(owner_id=owner_id)
        with open(filename, 'rb') as f:
            r2 = self.post_files(r1['upload_url'], {'photo': f})
        if caption:
            r2['caption'] = caption
        r3 = self.photos_saveWallPhoto(**r2)[0]
        return 'photo%s_%s' % (r3['owner_id'], r3['id'])


def main():
    logging.basicConfig(level=logging.DEBUG)
    proxies = {'https': 'socks5://127.0.0.1:9050'}
    cdn = APISession(proxies=proxies)
    for i in BoorySearch(proxies=proxies, q='safe, -animated', sf='score', sd='desc'):
        url = i['representations']['large']
        filename = url.split('/')[-2]
        cdn.download_file(url, filename)


if __name__ == '__main__':
    main()
