# -*- coding: utf-8 -*-
from logging import getLogger
from dateutil.parser import parse
from .common import ApiObject, ApiException, ApiClient
log = getLogger('copydog.api')


class TrelloException(ApiException):
    pass


class Trello(ApiClient):

    def __init__(self, api_key=None, token=None):
        """ Creates api client instance.

        :param api_key: Developer API key for Trello. Can be obtained at https://trello.com/1/appKey/generate
        :param token: Authorization token with read or read-write access for some period of time
                https://trello.com/docs/gettingstarted/index.html#token
        """
        self.api_key = api_key
        self.token = token
        self.host = 'https://api.trello.com/1/'

    def default_payload(self):
        return dict(key=self.api_key, token=self.token)

    def build_api_url(self, path):
        return '{host}/{path}'.format(host=self.host.strip('/'), path=path)

    def get_many(self, path, **payload):
        json = self.method('get', path, **payload)
        for item in json:
            yield item

    def boards(self):
        """ Get a list of boards
        """
        for data in self.get_many('members/me/boards/'):
            yield Board(self, **data)

    def lists(self, board_id):
        """ Get list of lists :)
        """
        for data in self.get_many('boards/{board_id}/lists'.format(board_id=board_id)):
            yield List(self, **data)

    def members(self, board_id):
        """ Get list of lists :)
        """
        for data in self.get_many('boards/{board_id}/members'.format(board_id=board_id)):
            yield Member(self, **data)

    def cards(self, board_id, **kwargs):
        """ Get a list of cards

        :param board_id: The id of board to look for cards
        """
        updated__after = kwargs.pop('updated__after', None)
        num_cards_recieved = 0

        for data in self.get_many('boards/{board_id}/cards'.format(board_id=board_id), **kwargs):
            num_cards_recieved += 1
            card = Card(self, **data)
            if updated__after and card.last_updated <= updated__after:
                continue
            yield card

        log.debug('Got whole lot of %s cards from Trello board', num_cards_recieved)


class Board(ApiObject):
    """ Trello board """
    pass


class List(ApiObject):
    """ Trello list """
    pass


class Member(ApiObject):
    """ Trello board """
    pass


class Card(ApiObject):
    """ Trello card

        :param id: (optional) card's unique hash
        :param name: card's name
        :param desc: (optional) description
        :param idList: list id
        :param url: (optional) URL
    """

    def validate(self):
        assert self.name is not None
        assert self.idList is not None

    def get_url(self):
        return self.url

    def save(self):
        """ Save new card
        """
        if self.get('id'):
            result = self.client.put(path='cards/{card_id}'.format(card_id=self.id), data=self._data)
        else:
            result = self.client.post(path='cards', data=self._data)
            # Trello doesn't allow to assign cards on creation
            if self.get('idMembers'):
                self.client.post(path='cards/{card_id}/members'.format(card_id=result['id']),
                                 data={'value': self.idMembers[0]})
                result['idMembers'] = self.idMembers
        self._data = result
        return self

    def fetch(self):
        """ Fetch fresh info about the card

        We need it, because save method doesn't return card timestamp.
        """
        result = self.client.get('cards/{card_id}'.format(card_id=self.id), actions='all')
        self._data = result
        return self

    @property
    def last_updated(self):
        return parse(self.actions[0]['date'])

