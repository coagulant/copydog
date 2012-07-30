# -*- coding: utf-8 -*-
from copydog.api.redmine import Issue
from copydog.api.trello import Card


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
        if len(card.idMembers):
            assigned_to_id = self.storage.get_user_or_member_id(service_from, card.idMembers[0])
        else:
            assigned_to_id = None
        issue = Issue(
            id = self.storage.get_opposite_item_id(service_from, card.id),
            assigned_to_id = assigned_to_id,
            subject = card.name,
            description = card.desc,
            status_id = self.storage.get_list_or_status_id(service_from, card.idList),
            project_id = self.config.require('clients.redmine.project_id'),
            due_date = card.get('due'),
            client = self.clients[service_to]
        )
        return issue