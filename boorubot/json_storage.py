# coding: utf-8
import gzip
from json import JSONDecoder, JSONEncoder


# delme
class DB(object):
    def __init__(self, filename):
        self.filename = '%s.json' % filename
        
    def load(self):
        with open(self.filename, 'r') as f:
            data = f.read()
        return JSONDecoder().decode(data)
        
    def save(self, data):
        result = JSONEncoder().encode(data)
        with open(self.filename, 'w') as f:
            f.write(result)


class AbstractJsonStorage(object):
    ext = 'json'

    def __init__(self, filename):
        self.filename = '%s.%s' % (filename, self.ext)

    def load(self):
        return JSONDecoder().decode(self._read())

    def save(self, data):
        self._write(JSONEncoder().encode(data))

    def _read(self):
        raise NotImplementedError

    def _write(self, string):
        raise NotImplementedError


class JsonStorage(AbstractJsonStorage):
    def _read(self):
        with open(self.filename, 'r') as f:
            return f.read()

    def _write(self, string):
        with open(self.filename, 'w') as f:
            f.write(string)


class JsonStorageZip(AbstractJsonStorage):
    ext = 'json.gz'

    def _read(self):
        with gzip.open(self.filename, 'rb') as f:
            buf = f.read()
        return buf.decode('utf-8')

    def _write(self, string):
        buf = string.encode('utf-8')
        with gzip.open(self.filename, 'wb') as f:
            f.write(buf) 
