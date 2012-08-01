# -*- coding: utf-8 -*-
from logging import getLogger
from copydog.api.redmine import Issue
from copydog.api.trello import Card
log = getLogger('copydog')


class Mapper(object):

    def __init__(self, storage, clients, config=None):
        self.config = config
        self.storage = storage
        self.clients = clients

    def issue_to_trello(self, issue):
        assert isinstance(issue, Issue)
        service_from = 'redmine'
        service_to = 'trello'
        if hasattr(issue, 'assigned_to'):
            idMembers = [self.storage.get_user_or_member_id(service_from, issue.assigned_to['id'])]
        else:
            idMembers = [None]
        card = Card(
            id = self.storage.get_opposite_item_id(service_from, issue.id),
            idMembers = idMembers,
            name = issue.subject,
            desc = issue.get('description'),
            idList = self.storage.get_list_or_status_id(service_from, issue.status['id']),
            idBoard = self.config.require('clients.trello.board_id'),
            due = issue.get('due_date', 'null'),
            client = self.clients[service_to],
        )
        return card

    def card_to_redmine(self, card):
        assert isinstance(card, Card)
        service_from = 'trello'
        service_to = 'redmine'
        issue = Issue(
            id = self.storage.get_opposite_item_id(service_from, card.id),
            assigned_to_id = None,
            subject = card.name,
            description = card.desc,
            status_id = self.storage.get_list_or_status_id(service_from, card.idList),
            project_id = self.config.require('clients.redmine.project_id'),
            tracker_id = self.config.get('clients.redmine.tracker_id'),
            due_date = card.get('due'),
            client = self.clients[service_to]
        )
        if len(card.idMembers):
            issue.assigned_to_id = self.storage.get_user_or_member_id(service_from, card.idMembers[0])

        return issue

    def save_list_status_mapping(self):
        """ TODO: Optimize lookup
        """
        statuses = self.clients['redmine'].statuses()
        lists = self.clients['trello'].lists(self.config.require('clients.trello.board_id'))
        for status in statuses:
            for list in lists:
                if status.name == list.name:
                    self.storage.set_list_or_status_id(redmine_id=status.id, trello_id=list.id)
                    log.debug('Mapped Status %s to Trello', status.name)
                    break
            else:
                log.debug('Status %s not mapped to Trello', status.name)

    def save_user_member_mapping(self):
        users = self.clients['redmine'].users()
        members = self.clients['trello'].members(self.config.require('clients.trello.board_id'))
        for user in users:
            for member in members:
                if user.login == member.username or u'%s %s' % (user.firstname, user.lastname) == member.fullName:
                    self.storage.set_user_or_member_id(redmine_id=user.id, trello_id=member.id)
                    log.debug('Mapped User %s to Trello', user.login)
                    break
            else:
                log.debug('User %s not mapped to Trello', user.login)