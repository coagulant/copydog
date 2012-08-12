# -*- coding: utf-8 -*-
"""
Copydog syncs Redmine and Trello.

Usage:
  runner.py --config=<yaml> [options]
  runner.py (start|stop|restart) --config=<yaml> [options]
  runner.py (debug_storage|flush_storage) [options]

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
    config = Config()
    try:
        config = Config(file=config_path)
    except Exception as e:
        exit(str(e))

    config.full_sync = full_sync

    if not any(map(lambda item: item[1].get('write'), config.clients)):
        exit('Allow at least one client to write')

    watch = Watch(config)

    if daemonize:
        app = DeamonApp()
        app.run = watch.run
        DaemonRunner(app).do_action()
    else:
        watch.run()


def flush_storage():
    """ Erase all copydog keys and values from storage"""
    msg = 'This is irreversible operation, please confirm you want to empty copydog storage.'
    shall = True if raw_input("%s (y/N) " % msg).lower() == 'y' else False
    if shall:
        storage = Storage()
        storage.flush()
    else:
        print 'No action taken'


def main():
    arguments = docopt(__doc__, version='Copydog %s' % copydog.__version__)
    setup_logging(arguments)

    if arguments['debug_storage']:
        from copydog.utils import storage_browser
        storage_browser.main()
        exit()

    if arguments['flush_storage']:
        flush_storage()
        exit()

    full_sync = arguments['--fullsync']
    daemonize = bool(arguments.get('start') or arguments.get('stop') or arguments.get('restart'))
    execute(arguments['--config'], full_sync=full_sync, daemonize=daemonize)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
