# -*- coding: utf-8 -*-
import json
import logging
import pprint
from unittest.case import TestCase
import datetime
from dateutil.tz import tzoffset
import os
from copydog.api.redmine import Redmine, Issue


class TestRedmine(TestCase):

    def setUp(self):
        self.r = Redmine(host=os.environ.get('REDMINE_HOST'), api_key=os.environ.get('REDMINE_API_KEY'))

    def test_api(self):
        """ FIXME: no assert """
        r = Redmine(host='http://redmine.org', api_key=123)
        print r.issues()

    def test_protected_api(self):
        """ FIXME: no assert """
        print self.r.issues()

    def test_projects(self):
        """ FIXME: no assert """
        projects = self.r.projects()
        pprint.pprint(self.r.projects())

    def test_issues(self):
        """ FIXME: no assert """
        issues = self.r.issues(limit=1, tracker_name=u'Разработка')
        pprint.pprint(issues)

    def test_statuses(self):
        """ FIXME: no assert """
        statuses = self.r.statuses()
        pprint.pprint(statuses)

    def test_post(self):
        logging.basicConfig(level=logging.DEBUG)
#        issue = Issue(client=self.r, project_id='playground', subject=u"rrrr")
#        result = issue.save()
#
#        key = os.environ.get('REDMINE_API_KEY')
#        data = {"issue": {"due_date": None, "description": "Maybe card description will come later!\n",
#                          "status_id": "2", "assigned_to_id": "6", "project_id": "playground",
#                          "id": "6982", "subject": "Resolved card"}}
#        result = requests.put('https://fcdev.ru/issues/6982.json',
#                               data=json.dumps(data),
#                               headers={'Content-Type': 'application/json', 'X-Redmine-API-Key': key}
#        )
#        pprint.pprint(result.status_code)
#        pprint.pprint(result.content)
#        pprint.pprint(result.text)
#        pprint.pprint(result.json)



#        result = requests.post('https://fcdev.ru/issues.json?key=%s' % key,
#                               data=json.dumps({'issue': issue._data}),
#                               #headers={'Content-Type': 'application/json'}
#        )
#        pprint.pprint(result.status_code)
#        pprint.pprint(result.content)
#        pprint.pprint(result.text)




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

#    def test_save(self):
#        client = Redmine(host=os.environ.get('REDMINE_HOST'), api_key=os.environ.get('REDMINE_API_KEY'))
#        issue = Issue(client=client, subject='Test subject', description='Test description', project_id='playground')
#        issue.save()