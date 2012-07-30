# -*- coding: utf-8 -*-
from logging import getLogger
from api.redmine import Redmine
from storage import Storage, Mapper
from api.trello import Trello
log = getLogger('copydog')


class Watch(object):

    def __init__(self, config):
        log.info('Copydog is watching you...')
        self.config = config
        self.storage = Storage(self.config.get('storage'))
        clients_config = self.config.get_subconfig('clients')
        self.clients = {
            'redmine': Redmine(host=clients_config.require('redmine.host'),
                               api_key=clients_config.require('redmine.api_key')),
            'trello': Trello(api_key=clients_config.require('trello.api_key'),
                             token=clients_config.require('trello.token'))
        }
        self.mapper = Mapper(storage=self.storage, clients=self.clients, config=self.config)

    def save_list_status_mapping(self):
        """ TODO: Move mapping logic into Mapper class
            TODO: Optimize lookup
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
                log.warning('Status %s not mapped to Trello', status.name)

    def save_user_member_mapping(self):
        """ TODO: Move mapping logic into Mapper class
        """
        users = self.clients['redmine'].users()
        members = self.clients['trello'].members(self.config.require('clients.trello.board_id'))
        for user in users:
            for member in members:
                if user.login == member.username or u'%s %s' % (user.firstname, user.lastname) == member.fullName:
                    self.storage.set_user_or_member_id(redmine_id=user.id, trello_id=member.id)
                    log.debug('Mapped User %s to Trello', user.login)
                    break
            else:
                log.warning('User %s not mapped to Trello', user.login)

    def run(self):
        self.save_list_status_mapping()
        self.save_user_member_mapping()
        if self.config.get('clients.trello.write'):
            issues = self.read_redmine()
            if issues:
                self.write_trello(issues)

        if self.config.get('clients.redmine.write'):
            cards = self.read_trello()
            if cards:
                self.write_redmine(cards)

    def read_redmine(self):
        """ TODO: Check last_read against storage"""
        last_read = self.storage.get_last_time_read('redmine')
        issues = self.clients['redmine'].issues(updated__after=last_read,
                                                project_id=self.config.require('clients.redmine.project_id'))
        self.storage.mark_read('redmine', issues)
        timestamp = last_read.strftime('%Y-%m-%d %H:%M:%S') if last_read else 'Never'
        log.info('Read %s new issues from Redmine since %s', len(issues), timestamp)
        return issues

    def write_trello(self, issues):
        """ TODO: Make write fail-safe with retries"""
        for issue in issues:
            card = self.mapper.issue_to_trello(issue)
            log.debug('Saving issue %s to Trello', issue.id)
            log.debug('%s', card._data)
            card.save()
            card.fetch()
            log.debug('%s', card._data)
            self.storage.mark_written('trello', card, foreign_id=issue.id)
        log.info('Converted %s new issues to Trello', len(issues))

    def read_trello(self):
        last_read = self.storage.get_last_time_read('trello')
        cards = self.clients['trello'].cards(updated__after=last_read,
                                             board_id=self.config.require('clients.trello.board_id'),
                                             actions='all')
        self.storage.mark_read('trello', cards)
        timestamp = last_read.strftime('%Y-%m-%d %H:%M:%S') if last_read else 'Never'
        log.info('Read %s new cards from Trello since %s', len(cards), timestamp)
        return cards

    def write_redmine(self, cards):
        for card in cards:
            log.debug('%s', card._data)
            issue = self.mapper.card_to_redmine(card)
            log.debug('Saving card %s to Redmine', card.id)
            log.debug('%s', issue._data)
            issue.save()
            issue.fetch()
            log.debug('%s', issue._data)
            self.storage.mark_written('redmine', issue, foreign_id=card.id)
        log.info('Converted %s new cards to Redmine', len(cards))