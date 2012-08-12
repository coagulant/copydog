# -*- coding: utf-8 -*-
from logging import getLogger
from api.trello import Trello
from api.redmine import Redmine
from copydog.api.redmine import Issue
from copydog.api.trello import Card

log = getLogger('copydog')


class BaseAdapter(object):
    service_name = None
    writable = False

    def __init__(self, options, storage):
        self.config = options
        self.storage = storage
        self.client = self.get_client(options)

        self.writable = self.config.get('write')
        log.debug('%s is %swritable' % (self.service_name, 'not ' if not self.writable else ''))

    def __str__(self):
        return self.service_name

    def get_client(self, options):
        """ Instantiate remote API
        """
        raise NotImplemented

    def read(self):
        """ Read issues suitable for syncing from client
        """
        last_time_read = self.storage.get_last_time_read(self.service_name)
        log.debug('Reading %s since %s' % (self.service_name, last_time_read))
        issues = self.get_issues_since_last_sync(last_time_read)
        return issues

    def mark_read(self, issue):
        self.storage.mark_read(self.service_name, issue)

    def get_issues_since_last_sync(self, last_read):
        """ Client-specific API call
        """
        raise NotImplemented

    def convert_to_local_issue(self, foreign_issue):
        raise NotImplemented

    def add_foreign_issue_reference(self, issue, foreign_issue):
        raise NotImplemented

    def write(self, foreign_issue):
        """ Write items from other service to client
        """
        log.debug('Saving issue %s to %s', foreign_issue.id, self.service_name)
        log.debug('%s', foreign_issue._data)
        local_issue = self.convert_to_local_issue(foreign_issue)
        log.debug('%s', local_issue)
        local_issue.save()
        if local_issue.is_created():
            self.add_foreign_issue_reference(issue=local_issue, foreign_issue=foreign_issue)
        local_issue.fetch()
        self.storage.mark_written(self.service_name, local_issue, foreign_id=foreign_issue.id)


class RedmineAdapter(BaseAdapter):
    service_name = 'redmine'

    def get_client(self, options):
        return Redmine(host=options['host'], api_key=options['api_key'])

    def get_issues_since_last_sync(self, last_read):
        issues = self.client.issues(
            updated__after=last_read,
            tracker_id=self.config.get('tracker_id'),
            project_id=self.config.get('project_id'),
            fixed_version_id=self.config.get('fixed_version_id')
        )
        return issues

    def convert_to_local_issue(self, foreign_issue):
        assert isinstance(foreign_issue, Card)
        service_from = 'trello'

        if len(foreign_issue.idMembers):
            assigned_to_id = self.storage.get_user_or_member_id(service_from, foreign_issue.idMembers[0])
        else:
            assigned_to_id = None

        issue = Issue(
            id = self.storage.get_opposite_item_id(service_from, foreign_issue.id),
            assigned_to_id = assigned_to_id,
            subject = foreign_issue.name,
            description = foreign_issue.desc,
            status_id = self.storage.get_list_or_status_id(service_from, foreign_issue.idList),
            project_id = self.config.get('project_id'),
            tracker_id = self.config.get('tracker_id'),
            due_date = foreign_issue.get('due'),
            client = self.client
        )
        return issue

    def add_foreign_issue_reference(self, issue, foreign_issue):
        """ Currently can't update issue journal to leave a comment
            http://www.redmine.org/issues/10171
        """


class TrelloAdapter(BaseAdapter):
    service_name = 'trello'

    def get_client(self, options):
        return Trello(api_key=options['api_key'], token=options['token'])

    def get_issues_since_last_sync(self, last_read):
        issues = self.client.cards(
            updated__after=last_read,
            board_id=self.config.board_id,
            actions='all')
        return issues

    def convert_to_local_issue(self, foreign_issue):
        assert isinstance(foreign_issue, Issue)
        service_from = 'redmine'
        if hasattr(foreign_issue, 'assigned_to'):
            idMembers = [self.storage.get_user_or_member_id(service_from, foreign_issue.assigned_to['id'])]
        else:
            idMembers = [None]
        card = Card(
            id = self.storage.get_opposite_item_id(service_from, foreign_issue.id),
            idMembers = idMembers,
            name = foreign_issue.subject,
            desc = foreign_issue.get('description'),
            idList = self.storage.get_list_or_status_id(service_from, foreign_issue.status['id']),
            idBoard = self.config.board_id,
            due = foreign_issue.get('due_date', 'null'),
            client = self.client,
        )
        return card

    def add_foreign_issue_reference(self, issue, foreign_issue):
        """ Let's create a comment with redmine reference
            TODO: move .post into trello.py
        """
        text = '{service_name}: {issue_url}'.format(
            service_name=foreign_issue.client.service_name,
            issue_url=foreign_issue.get_url()
        )
        self.client.post(path='cards/{card_id}/actions/comments'.format(card_id=issue.id),
            data={'text': text})
