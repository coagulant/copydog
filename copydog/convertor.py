# -*- coding: utf-8 -*-
from copydog.trello import Card


class RedmineTrello(object):

    def __init__(self):
        pass

    def convert(self, issue):
        card = Card(
            id = None,
            idMembers = [None],
            desc = issue.description,
            idList = None,
            idBoard = None,
            name = issue.title,
            due = issue.deadline,
        )
        return card