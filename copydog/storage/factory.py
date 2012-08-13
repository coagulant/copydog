# -*- coding: utf-8 -*-
from exceptions import ImportError, Exception


class StorageFactory(object):
    default_backend = 'redis'

    @classmethod
    def get_class_name(cls, storage_name):
        if '.' not in storage_name:
            module_name = 'copydog.storage.backends.{0}_backend'.format(storage_name)
            class_name = 'Storage'
        else:
            module_name = storage_name[:storage_name.rfind(".")]
            class_name = storage_name[storage_name.rfind(".") + 1:]
        module = __import__(module_name, globals(), locals(), [class_name, ])
        storage_klass = getattr(module, class_name)
        return storage_klass

    @classmethod
    def get(cls, storage_config):
        try:
            if storage_config:
                storage_name = storage_config.keys()[0]
                options = storage_config[storage_name]
            else:
                storage_name = cls.default_backend
                options = None
            storage_klass = cls.get_class_name(storage_name)
            return storage_klass(storage_options=options)
        except ImportError as e:
            raise Exception('Copydog storage in not configured properly: %s' % str(e))