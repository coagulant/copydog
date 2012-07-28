# -*- coding: utf-8 -*-
from texttable import Texttable
from ..storage import Storage


def print_table(prefix, items):
    table = Texttable(max_width=160)
    table.set_deco(Texttable.HEADER)
    table.header(['%s_id' % prefix, '%s_updated' % prefix, '%s_fk' % prefix])
    for key, values in items.iteritems():
        table.add_row([key, values.get('updated'), values.get('opposite_id')])
    print table.draw() + "\n"


def print_list_mapping(prefix, items):
    table = Texttable(max_width=160)
    table.set_deco(Texttable.HEADER)
    table.header(['%s_liststatus_id' % prefix,  '%s_fk' % prefix])
    for key, value in items.iteritems():
        table.add_row([key, value])
    print table.draw() + "\n"


def main():
    storage = Storage()
    redmine_keys = storage.redis.keys(pattern='redmine:items*')
    trello_keys = storage.redis.keys(pattern='trello:items*')
    redmine_list_mapping = storage.redis.hgetall('redmine:list_status_mapping')
    trello_list_mapping = storage.redis.hgetall('trello:list_status_mapping')

    issues = dict((key, storage.redis.hgetall(key)) for key in redmine_keys)
    cards = dict((key, storage.redis.hgetall(key)) for key in trello_keys)

    print 'Copydog storage'
    print '==============='

    print 'Redmine last read at %s' % storage.get_last_time_read('redmine')
    print 'Trello last read at %s \n' % storage.get_last_time_read('trello')

    print_list_mapping('redmine', redmine_list_mapping)
    print_list_mapping('trello', trello_list_mapping)

    print_table('redmine', issues)
    print_table('trello', cards)



#if __name__ == "__main__":
#    main()
