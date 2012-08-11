# -*- coding: utf-8 -*-
from logging import getLogger
from copydog.api.redmine import Issue
from copydog.api.trello import Card
log = getLogger('copydog')


class Mapper(object):
    """
        TODO: remove hardcoded services
    """

    def __init__(self, storage, services, config=None):
        self.config = config
        self.storage = storage
        self.services = services

    def save_list_status_mapping(self):
        """ TODO: Optimize lookup
        """
        statuses = self.services['redmine'].client.statuses()
        lists = self.services['trello'].client.lists(self.config.clients.trello.board_id)
        for status in statuses:
            for list in lists:
                if status.name == list.name:
                    self.storage.set_list_or_status_id(redmine_id=status.id, trello_id=list.id)
                    log.debug('Mapped Status %s to Trello', status.name)
                    break
            else:
                log.debug('Status %s not mapped to Trello', status.name)

    def save_user_member_mapping(self):
        users = self.services['redmine'].client.users()
        members = self.services['trello'].client.members(self.config.clients.trello.board_id)
        for user in users:
            for member in members:
                if user.login == member.username or u'%s %s' % (user.firstname, user.lastname) == member.fullName:
                    self.storage.set_user_or_member_id(redmine_id=user.id, trello_id=member.id)
                    log.debug('Mapped User %s to Trello', user.login)
                    break
            else:
                log.debug('User %s not mapped to Trello', user.login)