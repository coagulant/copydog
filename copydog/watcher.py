# -*- coding: utf-8 -*-
from logging import getLogger
import time
import sched
from api.redmine import Redmine
from copydog.convertor import Mapper
from copydog.utils.task import periodic
from storage import Storage
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
        self.mapper.save_list_status_mapping()
        self.mapper.save_user_member_mapping()

    def sync(self):
        if self.config.get('clients.trello.write'):
            issues = self.read_redmine()
            if issues:
                self.write_trello(issues)

        if self.config.get('clients.redmine.write'):
            cards = self.read_trello()
            if cards:
                self.write_redmine(cards)

    def run(self):
        scheduler = sched.scheduler(time.time, time.sleep)
        periodic(scheduler, 60, self.sync)
        scheduler.run()

    def read_redmine(self):
        """ TODO: Check last_read against storage"""
        last_read = self.storage.get_last_time_read('redmine')
        issues = self.clients['redmine'].issues(updated__after=last_read,
                                                tracker_id=self.config.get('clients.redmine.tracker_id'),
                                                project_id=self.config.require('clients.redmine.project_id'),
                                                fixed_version_id=self.config.get('clients.redmine.fixed_version_id')
        )
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