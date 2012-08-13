# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class BaseStorage(object):
    """ Abstract storage class"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def flush(self):
        """ Empty storage, as if copydog never launched.
            Handly for debugging and cleaning up the mess.
        """

