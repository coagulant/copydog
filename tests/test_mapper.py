# -*- coding: utf-8 -*-
from unittest import TestCase
import datetime
from mock import Mock, patch
from copydog.adapters import RedmineAdapter, TrelloAdapter
from copydog.api.redmine import Issue
from copydog.convertor import Mapper
from copydog.api.trello import Card
from copydog.utils.config import Config
config = Config(file='examples/copydog.yml')
redmine_options = config.clients.redmine
trello_options = config.clients.trello


class IssueToCardTest(TestCase):

    def setUp(self):
        self.storage_mock = Mock()
        self.adapter = TrelloAdapter(trello_options, self.storage_mock)
        self.issue = Issue(**{
            'id': 6571,
            'subject': 'Save humanity',
            'description': 'Humanity in danger',
            'due_date': datetime.date(2012, 12, 20),
            'status': {'name': "Assigned", 'id': 2},
            'assigned_to': {'id': '42'}
        })

    @property
    def trello_card(self):
        return self.adapter.convert_to_local_issue(self.issue)

    def test_new_card_id(self):
        self.storage_mock.get_opposite_item_id.return_value = '777'
        self.assertEqual(self.trello_card.id, '777')

    def test_card_idMembers(self):
        self.storage_mock.get_user_or_member_id.return_value = 'abcdef'
        self.assertEqual(self.trello_card.idMembers, ['abcdef'])

    def test_card_name(self):
        self.assertEqual(self.trello_card.name, 'Save humanity')

    def test_card_desc(self):
        self.assertEqual(self.trello_card.desc.strip(), 'Humanity in danger')

    def test_id_list(self):
        self.storage_mock.get_list_or_status_id.return_value = '123'
        self.assertEqual(self.trello_card.idList, '123')

    @patch.object(trello_options, 'board_id', '1fe889e4c23b476f4a189ca5')
    def test_idBoard(self):
        self.assertEqual(self.trello_card.idBoard, '1fe889e4c23b476f4a189ca5')

    def test_due(self):
        self.assertEqual(self.trello_card.due, datetime.date(2012, 12, 20))

    def test_client(self):
        self.assertEqual(self.trello_card.client.service_name, 'trello')






class CardToIssueTest(TestCase):
    def setUp(self):
        self.storage_mock = Mock()
        options = Config({'host': 'xxx', 'api_key': 'yyy'})
        self.adapter = RedmineAdapter(redmine_options, self.storage_mock)
        self.issue = Card(**{
            'id': 'a84d79f572fbe7512b999c6b3cd7667cbe3138ff',
            'name': 'Destroy humanity',
            'desc': 'Humanity in our enemy',
            'due': datetime.date(1990, 1, 1),
            'idList': '4fe889e4c23b476f4a189ca6',
            'idMembers': [None],
        })

    @property
    def redmine_issue(self):
        return self.adapter.convert_to_local_issue(self.issue)

    def test_new_issue_id(self):
        self.storage_mock.get_opposite_item_id.return_value = '555'
        self.assertEqual(self.redmine_issue.id, '555')

    def test_issue_assigned_to(self):
        self.storage_mock.get_user_or_member_id.return_value = 42
        self.assertEqual(self.redmine_issue.assigned_to_id, 42)

    def test_issue_subject(self):
        self.assertEqual(self.redmine_issue.subject, 'Destroy humanity')

    def test_issue_description(self):
        self.assertEqual(self.redmine_issue.description.strip(), 'Humanity in our enemy')

    def test_status(self):
        self.storage_mock.get_list_or_status_id.return_value = '123'
        self.assertEqual(self.redmine_issue.status_id, '123')

    @patch.object(redmine_options, 'project_id', 7)
    def test_project_id(self):
        self.assertEqual(self.redmine_issue.project_id, 7)

    def test_due_date(self):
        self.assertEqual(self.redmine_issue.due_date, datetime.date(1990, 1, 1))

    def test_client(self):
        self.assertEqual(self.redmine_issue.client.service_name, 'redmine')

