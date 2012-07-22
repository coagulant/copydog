# -*- coding: utf-8 -*-
import pprint
from unittest.case import TestCase
import os
from copydog.trello import Trello


class TestTrello(TestCase):

    def setUp(self):
        self.trello = Trello(api_key=os.environ.get('TRELLO_API_KEY'),
                             token=os.environ.get('TRELLO_TOKEN'),
        )

    def test_trello(self):
        print self.trello.boards()