# -*- coding: utf-8 -*-
import pprint
from unittest.case import TestCase
import os
from copydog.redmine import Redmine


class TestRedmine(TestCase):

    def setUp(self):
        self.r = Redmine(host=os.environ.get('REDMINE_HOST'), api_key=os.environ.get('REDMINE_API_KEY'))

    def test_api(self):
        r = Redmine(host='http://redmine.org', api_key=123)
        print r.issues()

    def test_protected_api(self):
        print self.r.issues()

    def test_projects(self):
        projects = self.r.projects()
        pprint.pprint(self.r.projects())

    def test_issues(self):
        issues = self.r.issues(limit=1, tracker_name=u'Разработка')
        pprint.pprint(issues)