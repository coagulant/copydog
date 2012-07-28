# -*- coding: utf-8 -*-
from unittest.case import TestCase
import os
from copydog.api.trello import Trello


class TestTrello(TestCase):

    def setUp(self):
        self.trello = Trello(api_key=os.environ.get('TRELLO_API_KEY'),
                             token=os.environ.get('TRELLO_TOKEN'),
        )

    def test_trello(self):
        print self.trello.boards()

    def test_statuses(self):
        for list in self.trello.lists(board_id='4fe889e4c23b476f4a189ca5'):
            print list._data