# -*- coding: utf-8 -*-
"""
Copydog syncs Redmine and Trello.

Usage:
  runner.py watch --config=<yaml> [options]
  runner.py debug_storage [--config=<yaml>] [options]
  runner.py flush_storage [--config=<yaml>] [options]

Options:
  --config=<yaml>  Config file.
  -v --verbose     Make verbose output.
  -q --quiet       Make no output.
  -h --help        Show this screen.
  --version        Show version.
"""

import logging
from logging.config import dictConfig
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


def run_watch(config_path):
    config = Config.from_yaml(config_path)
    if not config.get('clients.trello.write') and not config.get('clients.redmine.write'):
        exit('Allow at least one client write')
    watch = Watch(config)
    watch.run()


def flush_storage():
    storage = Storage()
    storage.flush()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Copydog %s' % copydog.__version__)
    setup_logging(arguments)

    if arguments['watch']:
        run_watch(arguments['--config'])

    if arguments['debug_storage']:
        storage_browser.main()

    if arguments['flush_storage']:
        flush_storage()




