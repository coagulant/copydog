# -*- coding: utf-8 -*-
import json
from logging import getLogger
from .api import ApiObject, ApiException, ApiClient
log = getLogger('copydog.api')


class RedmineException(ApiException):
    pass


class Redmine(ApiClient):
    """ Redmine API class """

    def __init__(self, host, api_key=None):
        """ Creates api client instance.

        :host: Full URL of redmine installation.
        :api_key: API key for Redmine. Can be obtained at http://<your_domain>/my/account
        """
        self.host = host
        self.api_key = api_key


    def default_payload(self):
        return {
            'key': self.api_key
        }

    def build_api_url(self, path):
        return '{host}/{path}.json'.format(host=self.host.strip('/'), path=path)

    def post(self, path, data=None, **payload):
        log.info(json.dumps(data))
        return self.method('post', path, json.dumps(data), headers={'Content-Type': 'application/json'}, **payload)

    def put(self, path, data=None, **payload):
        return self.method('put', path, json.dumps(data), headers={'Content-Type': 'application/json'}, **payload)

    def issues(self, inverse=None, updated__after=None, **kwargs):
        """ Get a list of issues

        :param page: (optional) page number
        :param offset: (optional) skip this number of issues in response
        :param limit: (optional) number of issues per page
        :param project_id: (optional) get issues from the project with the given id,
                           where id is either project id or project identifier
        :param tracker_id: (optional) get issues from the tracker with the given id
        :param updated__after: (optional) only issues, update after given timestamp
        :param sort: (optional) column to sort with
        :param inverse: (optional) inverse sorting
        :type inverse: boolean
        """
        if inverse and kwargs.get('sort'):
            kwargs['sort'] += ':desc'
        if updated__after:
            kwargs['updated_on'] = '>={0}'.format(updated__after.date().isoformat())

        issues = self.get('issues', **kwargs)['issues']
        return [Issue(self, **data) for data in issues]

    def projects(self):
        """ Get a list of projects
        """
        projects = self.get('projects')['projects']
        return [Project(self, **data) for data in projects]

    def trackers(self):
        """ Get a list of trackers
        """
        trackers = self.get('trackers')['trackers']
        return [Tracker(self, **data) for data in trackers]

    def statuses(self):
        """ Get a list of statuses

        Ref: http://www.redmine.org/projects/redmine/wiki/Rest_IssueStatuses
        """
        statuses = self.get('issue_statuses')['issue_statuses']
        return [Status(self, **data) for data in statuses]


class Project(ApiObject):
    """ Redmine project"""


class Tracker(ApiObject):
    """ Redmine tracker"""


class Status(ApiObject):
    """ Redmine status"""


class Issue(ApiObject):
    """ Redmine issue

        :param id: issue's unique id
        :param subject: issue name
        :param description: description
    """
    date_fields = ('updated_on', 'created_on')

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
            result = self.client.put(path='issues/{issue_id}'.format(issue_id=self.id), data={'issue': self._data})
        else:
            result = self.client.post(path='issues', data={'issue': self._data})

        self._data = result
        return result


    @property
    def last_updated(self):
        return self.updated_on

