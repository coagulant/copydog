# -*- coding: utf-8 -*-
from unittest.case import TestCase
import datetime
from dateutil.tz import tzoffset
from nose.plugins.attrib import attr
import os
from copydog.api.redmine import Redmine, Issue


@attr('http', 'redmine')
class TestRedmine(TestCase):
    """ Make sure to provide ``REDMINE_HOST`` and ``REDMINE_API_KEY``
        environment variables to execute this test.
    """

    def setUp(self):
        self.r = Redmine(host=os.environ.get('REDMINE_HOST'),
                         api_key=os.environ.get('REDMINE_API_KEY'))

    def test_connect_public_api(self):
        r = Redmine(host='http://redmine.org')
        issues = r.issues()
        self.assertTrue(type(issues) is list)
        self.assertTrue(len(issues) > 0)

    def test_connect_protected_api(self):
        issues = self.r.issues()
        self.assertTrue(type(issues) is list)

    def test_projects(self):
        projects = self.r.projects()
        self.assertTrue(type(projects) is list)

    def test_issues(self):
        issues = self.r.issues(limit=1)
        self.assertTrue(type(issues) is list)
        self.assertTrue(len(issues) <= 1)

    def test_statuses(self):
        statuses = self.r.statuses()
        self.assertTrue(type(statuses) is list)


@attr('redmine')
class TestIssue(TestCase):

    def test_init(self):
        json = {u'status': {u'name': u'Assigned', u'id': 2},
                u'due_date': u'2012/07/23',
                u'description': u"Issue's description",
                u'author': {u'name': u'\u0418\u043b\u044c\u044f \u0411\u0430\u0440\u044b\u0448\u0435\u0432',
                            u'id': 3},
                u'project': {u'name': u'Test', u'id': 40},
                u'created_on': u'2012/07/22 16:17:37 +0400',
                u'tracker': {u'name': u'\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
                             u'id': 8},
                u'custom_fields': [{u'name': u'\u041f\u0440\u0438\u0451\u043c\u043e\u0447\u043d\u044b\u0439 \u0442\u0435\u0441\u0442',
                                    u'value': u'', u'id': 3}],
                u'assigned_to': {u'name': u'\u0418\u043b\u044c\u044f \u0411\u0430\u0440\u044b\u0448\u0435\u0432',
                                 u'id': 3},
                u'updated_on': u'2012/07/22 21:56:52 +0400',
                u'subject': u'First issue',
                u'id': 6844,
                u'done_ratio': 0,
                u'priority': {u'name': u'\u041d\u043e\u0440\u043c\u0430\u043b\u044c\u043d\u044b\u0439', u'id': 4}}
        self.assertEqual(Issue(**json).created_on, datetime.datetime(2012, 7, 22, 16,17,37, tzinfo=tzoffset(None, 14400)))