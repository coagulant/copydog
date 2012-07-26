# -*- coding: utf-8 -*-
import os
import yaml


class ImproperlyConfigured(Exception):
    """ Something wrong with config file"""


class Config(object):
    """  Config object for copydog"""

    def __init__(self, data):
        self._data = data

    @classmethod
    def from_yaml(cls, filepath):
        return cls(yaml.load(open(filepath)))

    def get_subconfig(self, name):
        return Config(self._data[name])

    def get(self, path, default=None, fallback=True):
        try:
            result = self._data
            for part in path.split('.'):
                result = result[part]
            return result
        except KeyError:
            key = path.replace('.', '_').upper()
            if key in os.environ:
                return os.environ[key]
            if fallback:
                return default
            raise ImproperlyConfigured('Missing config %s' % path)

    def require(self, path):
        return self.get(path, fallback=False)
