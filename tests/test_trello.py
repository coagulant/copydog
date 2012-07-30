# -*- coding: utf-8 -*-
from unittest.case import TestCase
from nose.plugins.attrib import attr
import os
from copydog.api.trello import Trello


@attr('http', 'trello')
class TestTrello(TestCase):
    """ Make sure to provide ``TRELLO_API_KEY`` and ``TRELLO_TOKEN``
        environment variables to execute this test.
    """

    def setUp(self):
        self.trello = Trello(api_key=os.environ.get('TRELLO_API_KEY'),
                             token=os.environ.get('TRELLO_TOKEN'),
        )

    def test_trello_connect(self):
        boards = self.trello.boards()
        self.assertTrue(type(boards) is list)