# -*- coding: utf-8 -*-

def periodic(scheduler, interval, action, actionargs=()):
    scheduler.enter(interval, 1, periodic,
        (scheduler, interval, action, actionargs))
    action(*actionargs)