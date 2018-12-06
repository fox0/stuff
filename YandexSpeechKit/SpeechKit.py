#!/usr/bin/env python3
import warnings
import logging
# import logging.config
from uuid import uuid4
from xml.etree import ElementTree as Et
import requests

import yandex_pb2
try:
    from private_settings import key
except ImportError:
    warnings.warn('You must set key')
    key = ''

log = logging.getLogger(__name__)

UUID = uuid4().hex
PROXIES = {
    'http': '11.11.11.1:3128',
    'https': '11.11.11.1:3128',
}

# LOGGING = {
#     'version': 1,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         }
#     },
#     'loggers': {
#         '': {
#             'level': 'DEBUG',
#             'handlers': ['console'],
#         }
#     },
# }


def main():
    lang = 'ru-RU'
    # lang = 'en-US'
    with open('examples/speech.wav', 'rb') as f:
        r = requests.post('https://asr.yandex.net/asr_xml',
                          headers={'Content-Type': 'audio/x-wav'},
                          params=dict(uuid=UUID, key=key, topic='queries', lang=lang, disableAntimat=True),
                          data=f,
                          proxies=PROXIES
                          )
        r.raise_for_status()
        log.debug(r.text)
        import pprint
        pprint.pprint(parse_response(r.text))


def parse_response(xml):
    """

    :param xml:
    :return:

    Example
    <?xml version="1.0" encoding="utf-8"?>
    <recognitionResults success="1">
        <variant confidence="1">твой номер 212-85-06</variant>
    </recognitionResults>

    [('1', 'твой номер 212-85-06')]
    """
    result = []
    root = Et.fromstring(xml)
    for i in root.findall('./variant'):
        confidence = float(i.attrib['confidence'])
        result.append((confidence, i.text))
    return result


if __name__ == '__main__':
    # logging.config.dictConfig(LOGGING)
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                        level=logging.DEBUG)
    main()
