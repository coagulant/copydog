# -*- coding: utf-8 -*-
import datetime
from dateutil.parser import parse
import pytz
import redis
from copydog.redmine import Issue
from copydog.trello import Card


class Storage(object):

    def __init__(self, config=None):
        if not config:
            config  = {}
        self.redis = redis.StrictRedis(**config)

    def get_opposite_item_id(self, service_name, id):
        return self.redis.hget('{service_name}:items:{id}'.format(service_name=service_name, id=id), 'opposite_id')

    def get_list_or_status_id(self, service_name, id):
        return self.redis.hget('{service_name}:list_status_mapping'.format(service_name=service_name), id)

    def set_list_or_status_id(self, redmine_id, trello_id):
        pipe = self.redis.pipeline()
        pipe.hset('redmine:list_status_mapping', redmine_id, trello_id)
        pipe.hset('trello:list_status_mapping', trello_id, redmine_id)
        pipe.execute()

    def get_last_time_read(self, service_name):
        value = self.redis.get('{service_name}:last_read_time'.format(service_name=service_name))
        if value:
            return parse(value)
        return None

    def mark_read(self, service_name, items):
        pipe = self.redis.pipeline()
        pipe.set('{service_name}:last_read_time'.format(service_name=service_name),
            datetime.datetime.utcnow().replace(tzinfo = pytz.utc))
        for item in items:
            pipe.hset('{service_name}:items:{id}'.format(service_name=service_name, id=item.id),
                      'updated', item.last_updated)
        pipe.execute()

    def mark_written(self, service_name, item, foreign_id):
        other_service = 'redmine' if service_name == 'trello' else 'trello'
        pipe = self.redis.pipeline()
        pipe.hmset('{service_name}:items:{id}'.format(service_name=service_name, id=item.id),
                  {'opposite_id': foreign_id, 'updated': item.last_updated})
        pipe.hset('{other_service}:items:{id}'.format(other_service=other_service, id=foreign_id),
                  'opposite_id', item.id)
        pipe.execute()


class Mapper(object):

    def __init__(self, storage, clients, config=None):
        self.config = config
        self.storage = storage
        self.clients = clients

    def issue_to_trello(self, issue):
        assert isinstance(issue, Issue)
        service_from = 'redmine'
        service_to = 'trello'
        card = Card(
            id = self.storage.get_opposite_item_id(service_from, issue.id),
            idMembers = [None],
            name = issue.subject,
            desc = issue.description,
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
            assigned_to = None,
            subject = card.name,
            description = card.desc,
            status_id = self.storage.get_list_or_status_id(service_from, card.idList),
            project_id = self.config.require('clients.redmine.project_id'),
            due_date = card.get('due'),
            client = self.clients[service_to]
        )
        return issue