# -*- coding: utf-8 -*-
import os
import yaml

class ImproperlyConfigured(Exception):
    """ Something wrong with config file
    """

class MissigAttr(AttributeError):
    """ Config doesn't have specific value
    """

class Config(object):
    """ Object-like config with dict inside.
    """

    def __init__(self, data=None, file=None, name=''):
        if data and file:
            raise ImproperlyConfigured('Provide either data or filepath')
        if file:
            data = yaml.load(open(file))
        self.__data = data or {}
        self.__name = name

    def get(self, key, value=None):
        return self.__data.get(key, value)

    def __getattr__(self, name):
        try:
            attr = self.__data[name]
        except KeyError:
            return self.__getfallback(name)

        if type(attr) == dict:
            # creating subconfig
            return Config(attr, name=self.__getname(name))
        else:
            return attr

    def __getname(self, name):
        return '.'.join((self.__name, name)) if self.__name else name

    def __getfallback(self, name):
        env_var = ('%s_%s' % (self.__name.replace('.', '_'), name)).upper()
        if env_var in os.environ:
            return os.environ.get(env_var)
        raise MissigAttr('Missing config item %s' % self.__getname(name))

    def __str__(self):
        return self.__name

    def __iter__(self):
        for key in self.__data.iterkeys():
            yield key, self.__getattr__(key)