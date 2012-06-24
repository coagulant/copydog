# -*- coding: utf-8 -*-
import requests
import sys


class RedmineException(Exception):
    pass


class Redmine(object):
    """ Redmine API class """

    def __init__(self, host, api_key=None):
        """ Creates api client instance.

        :host: Full URL of redmine installation.
        :api_key: API key for Redmine. Can be obtained at http://<your_domain>/my/account
        """
        self.host = host
        self.api_key = api_key

    def _get(self, path, **payload):
        my_config = {'verbose': sys.stderr}
        url = '{host}/{path}.json'.format(host=self.host, path=path)
        headers = {'Content-Type': 'application/json'}
        payload.update(key=self.api_key)
        response = requests.get(url, params=payload, headers=headers, config=my_config)
        response.raise_for_status()
        if response.json:
            return response.json
        else:
            raise RedmineException

    def issues(self, **kwargs):
        """ Get a list of issues

        :param page: page number (optional)
        :param offset: skip this number of issues in response (optional)
        :param limit: number of issues per page (optional)
        :param project_id: get issues from the project with the given id, where id is either project id or project identifier
        :param tracker_id: get issues from the tracker with the given id
        """
        return self._get('issues', **kwargs)

    def projects(self):
        """ Get a list of projects
        """
        projects = self._get('projects')['projects']
        return [Project(self, project_data) for project_data in projects]


class ApiObject(object):
    def __init__(self, redmine, data):
        """ Project constructor.

        :param redmine: Redmine client
        :param data: project internals
        """
        self.__dict__.update(data)
        self.redmine = redmine

    def __repr__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u'<{0.__class__.__name__} {0.name}>'.format(self)


class Project(ApiObject):
    """ Project in Redmine"""



