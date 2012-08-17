# -*- coding: utf-8 -*-
from unittest import TestCase
from mock import patch
from copydog.utils.config import Config
from copydog.watcher import Watch
from copydog.bin.runner import execute


@patch('runner.Watch', spec=Watch)
@patch('runner.DaemonRunner')
class TestRunner(TestCase):

    def test_execute_runs_watch_by_default(self, daemon_mock, watch_mock):
        execute(Config(file='examples/copydog.yml'))
        self.assertTrue(watch_mock.called)
        watch_mock.return_value.run.assert_called_with()

    def test_execute_can_run_daemonized(self, daemon_mock, watch_mock):
        execute(Config(file='examples/copydog.yml'), daemonize=True)
        self.assertTrue(daemon_mock.called)
        self.assertFalse(watch_mock.return_value.run.called)



