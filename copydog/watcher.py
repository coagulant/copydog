# -*- coding: utf-8 -*-
from logging import getLogger
import time
import sched
import itertools
from copydog.utils import pandoc
from copydog.adapters import RedmineAdapter, TrelloAdapter
from copydog.convertor import Mapper
from copydog.storage.factory import StorageFactory
from copydog.utils.task import periodic


log = getLogger('copydog')


class Watch(object):
    available_services = {
        'redmine': RedmineAdapter,
        'trello': TrelloAdapter
    }

    def __init__(self, config, full_sync=False):
        log.info('Copydog is on duty...')
        self.storage = StorageFactory.get(config.get('storage'))
        self.services = self.setup_services(config, self.storage)
        self.setup_copydog(config.get('copydog'))
        self.setup_last_time_read(full_sync)
        self.mapper = Mapper(storage=self.storage, services=self.services, config=config)
        self.mapper.save_list_status_mapping()
        self.mapper.save_user_member_mapping()

    def setup_copydog(self, options=False):
        if not options:
            return
        if options.get('pandoc'):
            pandoc.PANDOC_PATH = options.get('pandoc')

    def setup_services(self, config, storage):
        clients_config = config.clients
        services = {}
        for service_name, options in clients_config:
            service_class = self.available_services[service_name]
            services[service_name] = service_class(options, storage)
        return services

    def setup_last_time_read(self, full_sync=False):
        """ Ignoring last time read, when using full_sync,
            If launching for first time, make sure we're monitoring only recent changes.

            TODO: remove hardcoded services
        """
        if full_sync:
            self.storage.reset_last_time_read()
        else:
            if not self.storage.get_last_time_read('redmine'):
                self.storage.mark_read('redmine')
                self.storage.mark_read('trello')

    def run(self):
        """ Run copydog in a loop, starting sync every 60 seconds.
        """
        scheduler = sched.scheduler(time.time, time.sleep)
        periodic(scheduler, 60, self.sync)
        scheduler.run()

    def sync(self):
        groups = itertools.groupby(itertools.permutations(self.services, 2), lambda pair:pair[0])
        for service_from_name, services in groups:
            service_from = self.services[service_from_name]
            issues = service_from.read()
            num_issues_read = 0
            services = list(services)
            for issue in issues:
                if self.is_already_synced(issue):
                    continue
                num_issues_read += 1
                service_from.mark_read(issue)
                for service_from_name, service_to_name in services:
                    service_to = self.services[service_to_name]
                    if service_to.writable:
                        service_to.write(issue)
            log.info('Read %s new issues from %s', num_issues_read, service_from)

    def is_already_synced(self, issue):
        """ Check issue needs sync

            Read from API last_updated > read from storage last_updated
            thus preventing clones
        """
        last_time_synced = self.storage.get_last_time_updated(issue.client.service_name, issue)
        log.debug('Comparing %s <= %s (%s)' % (issue.last_updated, last_time_synced,
            (last_time_synced and issue.last_updated <= last_time_synced)))
        return last_time_synced and issue.last_updated <= last_time_synced

