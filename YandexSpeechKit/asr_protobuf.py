#!/usr/bin/env python3
import warnings
import logging
import socket
import select
from uuid import uuid4
from yandex_pb2 import ConnectionRequest, ConnectionResponse, AddData, AddDataResponse

try:
    from private_settings import key
except ImportError:
    warnings.warn('You must set key')
    key = ''

log = logging.getLogger(__name__)

UUID = uuid4().hex


class YandexASR(object):
    BUFFER_SIZE = 64 * 1024

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connect()

    def _connect(self):
        self.socket.connect(('asr.yandex.net', 80))
        h = '\r\n'.join([
            'GET /asr_partial HTTP/1.1',
            'User-Agent: KeepAliveClient',
            'Host: asr.yandex.net',
            'Upgrade: dictation',
            '',
            '',
        ])
        log.debug('\n%s', h)
        self.socket.send(h.encode())
        buf = ''
        while True:
            buf += self.socket.recv(self.BUFFER_SIZE).decode()
            if '\r\n\r\n' in buf:
                break
        log.debug('\n%s', buf)
        ls = buf.split('\r\n')
        if ls[0] != 'HTTP/1.1 101 Switching Protocols':
            raise Exception()

    def send(self, message):
        # while True:
        #     r, w, x = select.select([], [self.socket], [self.socket], 0.1)
        #     if x:
        #         raise Exception()
        #     if w:
        #         break
        l = len(message)
        self.socket.send(('%x' % l).encode())
        self.socket.send(b'\r\n')
        self.socket.send(message)
        log.debug('send %d bytes', l)

    def recv(self):
        buf = bytearray()
        while True:  # todo loop
            d = self.socket.recv(self.BUFFER_SIZE)
            if not d:
                return None
            buf += d
            l, data = buf.split(b'\r\n', 1)
            l = int(b'0x' + l, 0)
            l2 = len(data)
            if l == l2:
                log.debug('recv %d bytes', l)
                return data
            else:
                log.debug('recv %d bytes of %d', l, l2)

    def close(self):
        self.socket.close()


def main():
    s = YandexASR()

    request = get_request()
    s.send(request.SerializeToString())

    response = ConnectionResponse()
    response.ParseFromString(s.recv())
    if response.responseCode != 200:  # ConnectionResponse.ResponseCode['OK']:
        raise Exception(response)

    with open('examples/speech.wav', 'rb') as f:
        content = f.read()

    chunked_size = 2 * 1024
    while True:
        l = len(content)
        if l <= 0:
            break
        data = AddData()
        data.audioData = content[:chunked_size]
        data.lastChunk = False

        while True:
            r, w, x = select.select([s.socket], [s.socket], [s.socket], 0.1)
            if r:
                response = AddDataResponse()
                d = s.recv()
                if d:
                    response.ParseFromString(d)
                    if response.responseCode != 200:
                        log.exception(response)
                    print(response)
            if w:
                s.send(data.SerializeToString())
                break
            if x:
                raise Exception()

        content = content[chunked_size:]

    data = AddData()
    data.lastChunk = True  # todo
    s.send(data.SerializeToString())

    response = s.recv()
    print(response)

    s.close()


def get_request():
    request = ConnectionRequest()
    request.speechkitVersion = ''
    request.serviceName = 'asr_dictation'
    request.uuid = UUID
    request.apiKey = key
    request.applicationName = 'fox 0.1'
    request.device = 'desktop'
    request.coords = '0,0'
    request.topic = 'queries'
    request.lang = 'ru-RU'
    # request.lang = 'en-US'
    # https://tech.yandex.ru/speechkit/cloud/doc/guide/concepts/asr-http-request-docpage/#audio-data-format
    request.format = 'audio/x-wav'
    request.disableAntimatNormalizer = True
    return request


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
