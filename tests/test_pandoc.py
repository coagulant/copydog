# -*- coding: utf-8 -*-
from unittest import TestCase
from mock import patch
from nose.plugins.attrib import attr
from copydog.utils.pandoc import convert


@attr('pandoc')
class PandocTest(TestCase):

    def test_pandoc(self):
        markdown_text = u"""\
Hello
=====
We're loving Markdown"""

        expected_result = u"""\
h1. Hello

We're loving Markdown

"""

        self.assertEqual(convert(markdown_text, 'markdown', 'textile'), expected_result)

    def test_unicode(self):
        unicode_text = u'Привет'
        self.assertEqual(convert(unicode_text, 'textile', 'markdown').strip(), unicode_text)

    @patch('copydog.utils.pandoc.PANDOC_PATH', '/tmp/')
    def test_not_installed(self):
        unicode_text = u'Hello _worlds_'
        self.assertEqual(convert(unicode_text, 'textile', 'markdown').strip(), unicode_text)