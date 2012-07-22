# -*- coding: utf-8 -*-
from .api import ApiObject, ApiException, ApiClient


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

    def boards(self):
        """ Get a list of boards
        """
        json = self.get('members/me/boards/')
        return [Board(self, **data) for data in json]

    def cards(self, board_id, **kwargs):
        """ Get a list of cards

        :param board_id: The id of board to look for cards
        """
        json = self.get('boards/{board_id}/cards/'.format(board_id=board_id))
        return [Card(self, **data) for data in json]


class Board(ApiObject):
    """ Trello board """

    def __init__(self, client, **data):
        super(Board, self).__init__(client, **data)


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

    def save(self):
        """ Save new card
        """
        if self.id:
            method = 'put'
        else:
            method = 'post'
        self.client.method(method, path='cards', data=self._data)


class List(ApiObject):
    """ Trello list"""