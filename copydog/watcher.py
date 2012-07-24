# -*- coding: utf-8 -*-
from logging import getLogger
from dateutil.parser import parse
from copydog.redmine import Redmine
from copydog.storage import Storage, Mapper
from copydog.trello import Trello
log = getLogger(__name__)


class Watch(object):

    def __init__(self, config):
        self.config = config
        self.storage = Storage()
        self.clients = {
            'redmine': Redmine(host=self.config.redmine_host, api_key=self.config.redmine_api_key),
            'trello': Trello(api_key=self.config.trello_api_key, token=self.config.trello_token)
        }
        self.mapper = Mapper(storage=self.storage, clients=self.clients, config=config)

    def run(self):
        issues = self.read_redmine()
        self.write_trello(issues)

        cards = self.read_trello()
        self.write_redmine(cards)

    def read_redmine(self):
        last_read = self.storage.get_last_time_read('redmine')
        issues = self.clients['redmine'].issues(updated__after=last_read,
                                                project_id=self.config.default_project_id)
        self.storage.mark_read('redmine', issues)
        log.debug('Read %s issues from Redmine since %s', len(issues), last_read)
        return issues

    def write_trello(self, issues):
        for issue in issues:
            card = self.mapper.issue_to_trello(issue)
            log.debug('Saving issue %s to Trello', issue.id)
            log.debug('%s', card._data)
            card.save()
            card.fetch()
            self.storage.mark_written('trello', card, foreign_id=issue.id)

    def read_trello(self):
        last_read = self.storage.get_last_time_read('trello')
        cards = self.clients['trello'].cards(updated__after=last_read,
                                             board_id=self.config.default_board_id, actions='all')
        self.storage.mark_read('trello', cards)
        return cards

    def write_redmine(self, cards):
        for card in cards:
            log.debug('%s', card._data)
            issue = self.mapper.card_to_redmine(card)
            log.debug('Saving card %s to Redmine', card.id)
            log.debug('%s', issue._data)
            issue.save()
            log.debug('%s', issue._data)
            self.storage.mark_written('redmine', issue, foreign_id=card.id)