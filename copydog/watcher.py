# -*- coding: utf-8 -*-
from logging import getLogger
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

        #cards = self.read_trello()
        #self.write_redmine(cards)

    def read_redmine(self):
        issues = self.clients['redmine'].issues(updated__after=self.storage.get_last_time_read('redmine'),
                                                project_id=self.config.default_project_id)
        self.storage.mark_read(issues)
        log.debug('Read %s issues from Redmine', len(issues))
        return issues

    def write_trello(self, issues):
        for issue in issues:
            card = self.mapper.issue_to_trello(issue)
            log.debug('%s', issue.__dict__)
            log.debug('Saving issue %s to Trello', issue.id)
            log.debug('%s', card._data)
            card.save()

    def read_trello(self):

        cards = self.clients['trello'].cards(board_id=self.config.default_board_id)
        return cards

    def write_redmine(self, cards):
        for card in cards:
            issue = card.as_card()
            print issue.save()
