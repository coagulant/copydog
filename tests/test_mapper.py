# -*- coding: utf-8 -*-
from unittest.case import TestCase
import datetime
from mock import Mock, patch
from copydog.redmine import Issue
from copydog.storage import Mapper
from copydog.trello import Card
from copydog.utils.config import Config
config = Config.from_yaml('tests/copydog.yml')


class MapperIssueToCardTest(TestCase):

    def setUp(self):
        self.storage_mock = Mock()
        self.mapper = Mapper(config=config,
            storage=self.storage_mock,
            clients={
                'redmine': Mock(return_value='redmine'),
                'trello': Mock(return_value='trello')
        })
        self.issue = Issue(**{
            'id': 6571,
            'subject': 'Save humanity',
            'description': 'Humanity in danger',
            'due_date': datetime.date(2012, 12, 20),
            'status': {'name': "Assigned", 'id': 2}
        })

    @property
    def trello_card(self):
        return self.mapper.issue_to_trello(self.issue)

    def test_new_card_id(self):
        self.storage_mock.get_opposite_item_id.return_value = '777'
        self.assertEqual(self.trello_card.id, '777')

    def test_card_idMembers(self):
        self.assertEqual(self.trello_card.idMembers, [None])

    def test_card_name(self):
        self.assertEqual(self.trello_card.name, 'Save humanity')

    def test_card_desc(self):
        self.assertEqual(self.trello_card.desc, 'Humanity in danger')

    def test_id_list(self):
        self.storage_mock.get_item_list_id.return_value = '123'
        self.assertEqual(self.trello_card.idList, '123')

#    @patch('config.board_id', '1fe889e4c23b476f4a189ca5')
#    def test_idBoard(self):
#        self.assertEqual(self.trello_card.idBoard, '1fe889e4c23b476f4a189ca5')

    def test_due(self):
        self.assertEqual(self.trello_card.due, datetime.date(2012, 12, 20))

    def test_client(self):
        self.assertEqual(self.trello_card.client(), 'trello')


class MapperCardToIssueTest(TestCase):
    def setUp(self):
        self.storage_mock = Mock()
        self.mapper = Mapper(config=config,
            storage=self.storage_mock,
            clients={
                'redmine': Mock(return_value='redmine'),
                'trello': Mock(return_value='trello')
            })
        self.issue = Card(**{
            'id': 'a84d79f572fbe7512b999c6b3cd7667cbe3138ff',
            'name': 'Destroy humanity',
            'desc': 'Humanity in our enemy',
            'due': datetime.date(1990, 1, 1),
            'idList': '4fe889e4c23b476f4a189ca6',
        })

    @property
    def redmine_issue(self):
        return self.mapper.card_to_redmine(self.issue)

    def test_new_card_id(self):
        self.storage_mock.get_opposite_item_id.return_value = '555'
        self.assertEqual(self.redmine_issue.id, '555')

    def test_card_idMembers(self):
        self.assertEqual(self.redmine_issue.assigned_to, None)

    def test_card_subject(self):
        self.assertEqual(self.redmine_issue.subject, 'Destroy humanity')

    def test_card_description(self):
        self.assertEqual(self.redmine_issue.description, 'Humanity in our enemy')

    def test_status(self):
        self.storage_mock.get_item_list_id.return_value = '123'
        self.assertEqual(self.redmine_issue.status_id, '123')

#    @patch('tests.config.CopyDogConfig.default_project_id', 7)
#    def test_project_id(self):
#        self.assertEqual(self.redmine_issue.project_id, 7)

    def test_due_date(self):
        self.assertEqual(self.redmine_issue.due_date, datetime.date(1990, 1, 1))

    def test_client(self):
        self.assertEqual(self.redmine_issue.client(), 'redmine')

