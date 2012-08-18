# -*- coding: utf-8 -*-
from unittest import TestCase
from nose.plugins.attrib import attr
import os
from copydog.api.trello import Trello, Board, Card, List, Member


@attr('http', 'trello')
class TestTrello(TestCase):
    """ Make sure to provide ``TRELLO_API_KEY`` and ``TRELLO_TOKEN``
        environment variables to execute this test.
    """

    def setUp(self):
        self.trello = Trello(api_key=os.environ.get('COPYDOG_TRELLO_API_KEY'),
                             token=os.environ.get('COPYDOG_TRELLO_TOKEN'),
        )
        self.board_id = '4d5ea62fd76aa1136000000c'

    def test_trello_connect(self):
        boards = self.trello.boards()
        self.assertTrue(next(boards, Board()), Board)

    def test_trello_cards(self):
        cards = self.trello.cards(board_id=self.board_id)
        self.assertTrue(next(cards), Card)

    def test_trello_lists(self):
        lists = self.trello.lists(board_id=self.board_id)
        self.assertTrue(next(lists), List)

    def test_trello_members(self):
        members = self.trello.lists(board_id=self.board_id)
        self.assertTrue(next(members), Member)