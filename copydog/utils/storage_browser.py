# -*- coding: utf-8 -*-
from texttable import Texttable


def print_table(prefix, items):
    table = Texttable(max_width=160)
    table.set_deco(Texttable.HEADER)
    table.header(['%s_id' % prefix, '%s_updated' % prefix, '%s_fk' % prefix])
    for key, values in items.iteritems():
        table.add_row([key, values.get('updated'), values.get('opposite_id')])
    print table.draw() + "\n"


def print_mapping(prefix, key, items):
    table = Texttable(max_width=160)
    table.set_deco(Texttable.HEADER)
    table.header(['%s_%s' % (prefix, key),  '%s_fk' % prefix])
    for key, value in items.iteritems():
        table.add_row([key, value])
    print table.draw() + "\n"


def browse(storage):
    redmine_keys = storage.redis.keys(pattern='redmine:items*')
    trello_keys = storage.redis.keys(pattern='trello:items*')
    redmine_list_mapping = storage.redis.hgetall('redmine:list_status_mapping')
    trello_list_mapping = storage.redis.hgetall('trello:user_member_mapping')
    redmine_user_mapping = storage.redis.hgetall('redmine:user_member_mapping')
    trello_user_mapping = storage.redis.hgetall('trello:user_member_mapping')

    issues = dict((key, storage.redis.hgetall(key)) for key in redmine_keys)
    cards = dict((key, storage.redis.hgetall(key)) for key in trello_keys)

    print 'Copydog storage'
    print '==============='

    print 'Redmine last read at %s' % storage.get_last_time_read('redmine')
    print 'Trello last read at %s \n' % storage.get_last_time_read('trello')

    print_mapping('redmine', 'list_status_id', redmine_list_mapping)
    print_mapping('trello', 'list_status_id', trello_list_mapping)

    print_mapping('redmine', 'user_member_id', redmine_user_mapping)
    print_mapping('trello', 'user_member_id', trello_user_mapping)

    print_table('redmine', issues)
    print_table('trello', cards)
