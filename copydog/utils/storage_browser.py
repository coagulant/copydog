# -*- coding: utf-8 -*-
import sys
sys.path.append('.')

from texttable import Texttable
from copydog.storage import Storage


def print_table(prefix, redmine_items):
    table = Texttable(max_width=160)
    table.header(['%s_id' % prefix, '%s_updated' % prefix, '%s_fk' % prefix])
    for key, values in redmine_items.iteritems():
        table.add_row([key, values.get('updated'), values.get('opposite_id')])
    print table.draw() + "\n"


def main():
    storage = Storage()
    redmine_keys = storage.redis.keys(pattern='redmine:items*')
    trello_keys = storage.redis.keys(pattern='trello:items*')

    issues = dict((key, storage.redis.hgetall(key)) for key in redmine_keys)
    cards = dict((key, storage.redis.hgetall(key)) for key in trello_keys)

    print 'Copydog storage'
    print '==============='

    print 'Redmine last read at %s' % storage.get_last_time_read('redmine')
    print 'Trello last read at %s' % storage.get_last_time_read('trello')

    print_table('redmine', issues)
    print_table('trello', cards)


if __name__ == "__main__":
    main()
