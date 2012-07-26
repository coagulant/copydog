# -*- coding: utf-8 -*-
"""
Copydog syncs Redmine and Trello.

Usage:
  watch.py --config=<yaml> [options]

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
from copydog.utils.config import Config, ImproperlyConfigured
from copydog.watcher import Watch


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Copydog %s' % copydog.__version__)
    logging.config.fileConfig('logging.cfg', disable_existing_loggers=True)

    if arguments['--verbose']:
        level = logging.DEBUG
    elif arguments['--quiet']:
        level = logging.CRITICAL
    else:
        level = logging.INFO
    logging.getLogger('copydog').setLevel(level)

    config = Config.from_yaml(arguments['--config'])
    if not config.get('clients.trello.write') and not config.get('clients.redmine.write'):
        exit('Allow at least one client write')

    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.DEBUG)

    watch = Watch(config)
    watch.run()



