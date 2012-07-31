# -*- coding: utf-8 -*-
"""
Copydog syncs Redmine and Trello.

Usage:
  runner.py --config=<yaml>
  runner.py (start|restart) --config=<yaml> [options]
  runner.py stop [options]
  runner.py debug_storage|flush_storage [options]

Options:
  --config=<yaml>  Config file.
  -v --verbose     Make verbose output.
  -q --quiet       Make no output.
  -h --help        Show this screen.
  --version        Show version.
"""

import logging
from logging.config import dictConfig
from daemon.runner import DaemonRunner
from docopt import docopt
import copydog
from copydog.storage import Storage
from copydog.utils import storage_browser
from copydog.utils.config import Config
from copydog.watcher import Watch


def setup_logging(arguments):
    logging.config.fileConfig('logging.cfg', disable_existing_loggers=True)
    if arguments['--verbose']:
        level = logging.DEBUG
    elif arguments['--quiet']:
        level = logging.CRITICAL
    else:
        level = logging.INFO
    logging.getLogger('copydog').setLevel(level)


def execute(config_path, daemonize=False):
    config = Config.from_yaml(config_path)
    if not config.get('clients.trello.write') and not config.get('clients.redmine.write'):
        exit('Allow at least one client write')
    watch = Watch(config)

    if not daemonize:
        watch.run()
    else:
        class DeamonApp(object):
            stdin_path='/tmp/copydog.in.log'
            stdout_path='/tmp/copydog.out.log'
            stderr_path='/tmp/copydog.err.log'
            pidfile_path='/tmp/copydog.pid'
            pidfile_timeout=100
            run=watch.run

        DaemonRunner(DeamonApp()).do_action()


def flush_storage():
    storage = Storage()
    storage.flush()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Copydog %s' % copydog.__version__)
    setup_logging(arguments)

    if arguments['debug_storage']:
        storage_browser.main()

    if arguments['flush_storage']:
        flush_storage()

    if arguments.get('start') or arguments.get('stop') or arguments.get('restart'):
        execute(arguments['--config'], daemonize=True)
    else:
        execute(arguments['--config'])




