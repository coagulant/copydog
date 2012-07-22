# -*- coding: utf-8 -*-
import os

class CopyDogConfig(object):
    default_board_id = '4fe889e4c23b476f4a189ca5'
    default_project_id = 'playground'

    redmine_host = os.environ.get('REDMINE_HOST')
    redmine_api_key = os.environ.get('REDMINE_API_KEY')

    trello_api_key =  os.environ.get('TRELLO_API_KEY')
    trello_token =  os.environ.get('TRELLO_TOKEN')