# -*- coding: utf-8 -*-
import os
import unittest
if not hasattr(unittest.TestCase, 'assertRaisesRegexp'):
    import unittest2 as unittest
from copydog.utils.config import Config, ImproperlyConfigured, MissigAttr


class ConfigInitTest(unittest.TestCase):
    example_yml = 'examples/copydog.yml'

    def test_empty_config_init(self):
        config = Config()
        self.assertEqual(config.get('option'), None)

    def test_config_init_dict(self):
        config = Config({'option': 'value'})
        self.assertEqual(config.get('option'), 'value')
        self.assertEqual(config.get('nonexistent'), None)
        self.assertEqual(config.get('nonexistent', False), False)

    def test_config_init_yml(self):
        config = Config(file=self.example_yml)
        self.assertTrue(type(config.get('clients')) is dict)
        self.assertSequenceEqual(config.get('clients').keys(), ('redmine', 'trello'))

    def test_bad_init(self):
        self.assertRaisesRegexp(ImproperlyConfigured, 'Provide either data or filepath',
                                Config, data={'option': 'value'}, file=self.example_yml)

def kwargs_test(**kwargs):
    return True


class ConfigAttrTest(unittest.TestCase):
    example_yml = 'examples/copydog.yml'

    def setUp(self):
        self.config = Config(file=self.example_yml)

    def test_attrs_scalar(self):
        self.assertEqual(self.config.clients.redmine.write, 1)

    def test_attr_subconfig(self):
        self.assertTrue(type(self.config.clients.trello), Config)
        self.assertTrue(kwargs_test(**self.config))

    def test_attr_nonexistent(self):
        with self.assertRaisesRegexp(MissigAttr, 'Missing config item clients.redmine.long_attr'):
            me = self.config.clients.redmine.long_attr

    def test_set_simple_attr(self):
        self.config.additional = 5
        self.assertEqual(self.config.additional, 5)
        self.assertEqual(self.config.get('additional'), None)

    def test_name(self):
        self.assertEqual(str(self.config), '')
        self.assertEqual(str(self.config.clients.redmine), 'clients.redmine')

    def test_iterable(self):
        for service, config in self.config.clients:
            self.assertTrue(type(service) is str)
            self.assertTrue(type(config) is Config)

    def test_env_fallback(self):
        os.environ.setdefault('COPYDOG_REDMINE_API_KEY', 'XXX')
        self.assertEqual(self.config.clients.redmine.api_key, 'XXX')
