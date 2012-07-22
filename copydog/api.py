# -*- coding: utf-8 -*-
from logging import getLogger
import requests
from requests.exceptions import HTTPError

log = getLogger(__name__)


class ApiException(Exception):
    """ Error, raised by API wrapper """


class ApiObject(object):
    def __init__(self, client=None, **data):
        """ Abstract API object constructor.

        :param client: API client
        :param data: object internals
        """
        self._data = data
        self.client = client
        self.__uid = data.get('name', data.get('id'))
        self.validate()
        log.debug('Created API object %s' % repr(self))

    def __getattr__(self, attr):
        return self._data[attr]

    def __repr__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u'<{class_name} {identifier}>'.format(class_name=self.__class__.__name__, identifier=self.__uid)

    def validate(self):
        """ Validate created object"""

    def as_dict(self):
        raise NotImplemented


class ApiClient(object):
    """ Base class for all service APIs"""

    def default_payload(self):
        return {}

    def build_api_url(self, path):
        raise NotImplemented

    def get(self, path, **payload):
        return self.method('get', path, **payload)

    def post(self, path, data=None, **payload):
        return self.method('get', path, data, **payload)

    def put(self, path, data=None, **payload):
        return self.method('get', path, data, **payload)

    def method(self, method, path, data=None, **payload):
        payload.update(self.default_payload())
        response = requests.request(method=method, url=self.build_api_url(path), data=data, params=payload)
        try:
            response.raise_for_status()
        except HTTPError as e:
            log.error(e.response.text)
            raise e

        if response.json:
            return response.json
        else:
            raise ApiException
