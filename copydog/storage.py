# -*- coding: utf-8 -*-
import datetime
from logging import getLogger
from dateutil.parser import parse
import pytz
import redis

log = getLogger('copydog')


class Storage(object):

    def __init__(self, config=None):
        if not config:
            config  = {}
        self.redis = redis.StrictRedis(**config)

    def get_opposite_item_id(self, service_name, id):
        return self.redis.hget('{service_name}:items:{id}'.format(service_name=service_name, id=id), 'opposite_id')

    def get_list_or_status_id(self, service_name, id):
        return self.redis.hget('{service_name}:list_status_mapping'.format(service_name=service_name), id)

    def set_list_or_status_id(self, redmine_id, trello_id):
        pipe = self.redis.pipeline()
        pipe.hset('redmine:list_status_mapping', redmine_id, trello_id)
        pipe.hset('trello:list_status_mapping', trello_id, redmine_id)
        pipe.execute()

    def get_user_or_member_id(self, service_name, id):
        return self.redis.hget('{service_name}:user_member_mapping'.format(service_name=service_name), id)

    def set_user_or_member_id(self, redmine_id, trello_id):
        """ TODO: extract method, set_list_or_status_id
        """
        pipe = self.redis.pipeline()
        pipe.hset('redmine:user_member_mapping', redmine_id, trello_id)
        pipe.hset('trello:user_member_mapping', trello_id, redmine_id)
        pipe.execute()

    def get_last_time_read(self, service_name):
        value = self.redis.get('{service_name}:last_read_time'.format(service_name=service_name))
        if value:
            return parse(value)
        return None

    def reset_last_time_read(self):
        self.redis.delete('{service_name}:last_read_time'.format(service_name='redmine'))
        self.redis.delete('{service_name}:last_read_time'.format(service_name='trello'))

    def mark_read(self, service_name, items):
        """ Returns number of read items
        """
        num_items_read = 0
        pipe = self.redis.pipeline()
        pipe.set('{service_name}:last_read_time'.format(service_name=service_name),
            datetime.datetime.utcnow().replace(tzinfo = pytz.utc))
        for item in items:
            pipe.hset('{service_name}:items:{id}'.format(service_name=service_name, id=item.id),
                      'updated', item.last_updated)
            num_items_read += 1
        pipe.execute()
        return num_items_read

    def mark_written(self, service_name, item, foreign_id):
        other_service = 'redmine' if service_name == 'trello' else 'trello'
        pipe = self.redis.pipeline()
        pipe.hmset('{service_name}:items:{id}'.format(service_name=service_name, id=item.id),
                  {'opposite_id': foreign_id, 'updated': item.last_updated})
        pipe.hset('{other_service}:items:{id}'.format(other_service=other_service, id=foreign_id),
                  'opposite_id', item.id)
        pipe.execute()

    def flush(self):
        redmine = self.redis.keys(pattern='redmine:*')
        trello = self.redis.keys(pattern='trello:*')
        keys_to_delete = redmine + trello
        if keys_to_delete:
            self.redis.delete(*keys_to_delete)
            log.debug('Deleted keys: %s', keys_to_delete)
            log.info('Deleted %d keys', len(keys_to_delete))
        else:
            log.info('Storage is empty')

