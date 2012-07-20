# -*- coding: utf-8 -*-
from unittest import TestCase
from copydog.convertor import RedmineTrello
from copydog.redmine import Issue


class Test(TestCase):

    def test_simple(self):
        issue = Issue(**{
            'id': 6571,
            'description': 'Hello World!',
            'title': 'My Title!',
            'deadline': None
        })
        convertor = RedmineTrello().convert(issue)

