# -*- coding: utf-8 -*-
import json
from logging import getLogger
from .common import ApiObject, ApiException, ApiClient
log = getLogger('copydog.api')


class RedmineException(ApiException):
    pass


class Redmine(ApiClient):
    """ Redmine API class """
    service_name = 'redmine'

    def __init__(self, host, api_key=None):
        """ Creates api client instance.

        :host: Full URL of redmine installation.
        :api_key: API key for Redmine. Can be obtained at http://<your_domain>/my/account
        """
        self.host = host.rstrip('/')
        self.api_key = api_key

    def default_payload(self):
        return {'key': self.api_key}

    def build_api_url(self, path):
        return '{host}/{path}.json'.format(host=self.host.strip('/'), path=path)

    def get_many(self, path, **payload):
        while True:
            data = self.method('get', path, **payload)
            for item in data[path]:
                yield item
            total_read = data.get('offset', 0) + data.get('limit', 0)
            if payload.get('limit') or total_read >= data.get('total_count', 0):
                break
            payload['offset'] = total_read

    def post(self, path, data=None, **payload):
        return self.method('post', path, json.dumps(data), headers={'Content-Type': 'application/json'}, **payload)

    def put(self, path, data=None, **payload):
        """ Redmine returns empty 200 OK"""
        return self.method('put', path, json.dumps(data), expect_json=False,
                           headers={'Content-Type': 'application/json'}, **payload)

    def issues(self, inverse=None, updated__after=None, **kwargs):
        """ Issue generator

        :param page: (optional) page number
        :param offset (optional): skip this number of issues in response
        :param limit (optional): number of issues per page
        :param project_id (optional): get issues from the project with the given id,
                           where id is either project id or project identifier
        :param fixed_version_id (optional): target version of the issues as a filter
        :param tracker_id (optional): get issues from the tracker with the given id
        :param updated__after (optional): only issues, update after given timestamp
        :param sort (optional): column to sort with
        :param inverse (optional): inverse sorting
        :type inverse: boolean

        Ref: http://www.redmine.org/projects/redmine/wiki/Rest_Issues
        """
        if inverse and kwargs.get('sort'):
            kwargs['sort'] += ':desc'
        if updated__after:
            kwargs['updated_on'] = '>={0}'.format(updated__after.date().isoformat())

        for data in self.get_many('issues', **kwargs):
            issue = Issue(self, **data)
            # Redmine doesn't allow granular search by timestamp, so filtering manually
            log.debug('Issue comparing %s > %s' % (issue.updated_on, updated__after))
            if updated__after and issue.updated_on <= updated__after:
                log.debug('ignoring')
                continue
            log.debug('passed')
            yield issue

    def projects(self):
        """ Get a list of projects
        """
        for data in self.get_many('projects'):
            yield Project(self, **data)

    def trackers(self):
        """ Get a list of trackers
        """
        for data in self.get_many('trackers'):
            yield Tracker(self, **data)

    def statuses(self):
        """ Get a list of statuses

        Ref: http://www.redmine.org/projects/redmine/wiki/Rest_IssueStatuses
        """
        for data in self.get_many('issue_statuses'):
            yield Status(self, **data)

    def users(self):
        """ Get a list of all users

        Ref: http://www.redmine.org/projects/redmine/wiki/Rest_Users
        """
        for data in self.get_many('users'):
            yield User(self, **data)


class Project(ApiObject):
    """ Redmine project"""


class Tracker(ApiObject):
    """ Redmine tracker"""


class Status(ApiObject):
    """ Redmine status"""


class User(ApiObject):
    """ Redmine user"""


class Issue(ApiObject):
    """ Redmine issue

        :param id: issue's unique id
        :param subject: issue name
        :param description: description
    """
    created = False
    date_fields = ('updated_on', 'created_on')

    def get_url(self):
        return '{host}/issues/{issue_id}/'.format(host=self.client.host, issue_id=self.id)

    def save(self):
        """ Save new issue

        Redmine expects:
        {
            "issue": {
                "project_id": "example",
                "subject": "Test issue",
                "custom_field_values":{
                    "1":"1.1.3"  #the affected version field
                }
            }
        }
        """
        if self.get('id'):
            result = self.client.put(path='issues/{issue_id}'.format(
                issue_id=self.id),
                data={'issue': self._data})
        else:
            result = self.client.post(path='issues', data={'issue': self._data})
            self._data = result['issue']
            self.created = True
        return self

    def fetch(self):
        """ Fetch fresh info about the issue

        We need it, because save method doesn't return card timestamp on PUT.
        """
        result = self.client.get('issues/{issue_id}'.format(issue_id=self.id))
        self._data = result['issue']
        return self

    @property
    def last_updated(self):
        return self.updated_on

    def is_created(self):
        return self.created
