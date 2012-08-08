# -*- coding: utf-8 -*-
"""
Copydog syncs Redmine and Trello.

Usage:
  runner.py --config=<yaml> [options]
  runner.py (start|stop|restart) --config=<yaml> [options]
  runner.py debug_storage|flush_storage [options]

Options:
  --config=<yaml>  Config file.
  -f --fullsync    Full sync (all issues, opposed to date range delta sync). Needed only once.
  -v --verbose     Make verbose output.
  -q --quiet       Make no output.
  -h --help        Show this screen.
  --version        Show version.
"""

import logging
import logging.config
from daemon.runner import DaemonRunner
from docopt import docopt
import copydog
from copydog.storage import Storage
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

class DeamonApp(object):
    stdin_path='/tmp/copydog.in.log'
    stdout_path='/tmp/copydog.out.log'
    stderr_path='/tmp/copydog.err.log'
    pidfile_path='/tmp/copydog.pid'
    pidfile_timeout=100
    run=lambda: None

def execute(config_path, full_sync=False, daemonize=False):
    try:
        config = Config.from_yaml(config_path)
    except Exception as e:
        exit(str(e))
    config.set('full_sync', full_sync)
    if not config.get('clients.trello.write') and not config.get('clients.redmine.write'):
        exit('Allow at least one client write')

    watch = Watch(config)

    if daemonize:
        app = DeamonApp()
        app.run = watch.run
        DaemonRunner(app).do_action()
    else:
        watch.run()


def flush_storage():
    storage = Storage()
    storage.flush()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Copydog %s' % copydog.__version__)
    setup_logging(arguments)

    if arguments['debug_storage']:
        from copydog.utils import storage_browser
        storage_browser.main()

    if arguments['flush_storage']:
        flush_storage()

    full_sync = arguments['--fullsync']
    daemonize = bool(arguments.get('start') or arguments.get('stop') or arguments.get('restart'))
    execute(arguments['--config'], full_sync=full_sync, daemonize=daemonize)

