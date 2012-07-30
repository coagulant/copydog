Copydog
-------

Copydog copies issues between Redmine_ and Trello_ on the fly.
It's a small daemon, monitoring changes in both systems and keeping
them in sync as much as possible.

.. toctree::
    index


Installation
============

Git clone the repo https://github.com/coagulant/copydog.git
You also need a redis instance to store sync intermediate results.

Configuration
=============

For copydog to work you obviously need both Trello and Redmine accounts.

Trello
^^^^^^
If you don't have an account, head over to `signup page`_ and register.
After that you need to obtain you API key and user token.

    * Generate_ the API key for your application (need to be logged in).

    * A token grants permissions (read, write or both) to one application
      for a specific user. To get a token for yourself, visit `the docs`_.

.. note::

    Obtain Trello token for forever read and write access::

        https://trello.com/1/authorize?key=substitutewithyourapplicationkey&name=My+Application&expiration=never&response_type=token&scope=read,write


Redmine
^^^^^^^
Copydog works with Redmine 1.3 and higher.
You'll be needing your redmine instance url and your API key.

To obtain the API key visit your profile page at redmine ``http://exampleredminehost/my/account``
and click ``Show link`` under ``API access key`` section.


Example config
^^^^^^^^^^^^^^
Copydog reads config variables from yaml files, so we need to make one.
Here is how config file might look like::

    clients:
        redmine:
            project_id: playground
            write: 1
        trello:
            board_id: 4fe889e4c23b476f4a189ca5
            write: 1
    storage:
        host: localhost
        port: 6379
        db: 0
        password:None

For now copydog supports syncing one redmine project with one trello board at a time,
so you need to specify ``project_id`` (string slug or integer) and ``board_id`` (string id).
Storage config might be completely omitted if you're using default Redis connection.
Write flag allows copydog to modify contents on a client, set it to 0
to disable sync writes to either redmine or trello.

Running copydog
===============
To launch the app::

    python runner.py --config=<path_to_your_yaml_config>

Copydog will start monitoring new changes in both services and mirror them accordingly.
Redmine statuses are associated with Trello lists and are mapped by exact name match,
so make sure you have same set of Statuses and Lists in your project and your board.
Assigned members are linked by username or full name as a fallback.

Fields
^^^^^^
Copydog tries to be smart when transferring cards to issues and vice versa:

============   ==========  =========
Redmine        Trello      Comment
============   ==========  =========
subject        name
description    desc
assigned_to    idMembers   Redmine doesn't support multiple assignees, the first one is taken.
status_id      isList      Copydog maps each status to list by name
project_id     board_id    For now, copydog allows to sync one board with one project only
due_date       due
============   ==========  =========

Launching tests
===============

To launch tests execute::

   nosetests

Some tests make actual API read requests, but they're disabled by default, to run them use::

   nosetests -c all

These tests will pass if you have following env variables set:

* ``REDMINE_HOST`` - the host of your redmine instance
* ``REDMINE_API_KEY`` - your API key to access Redmine API
* ``TRELLO_API_KEY`` - the API key  of your Trello app
* ``TRELLO_TOKEN`` - your consumer token to access Trello API


.. _Redmine: http://redmine.org/
.. _Trello: http://trello.com/
.. _generate: https://trello.com/1/appKey/generate
.. _the docs: https://trello.com/docs/gettingstarted/index.html#getting-a-token-from-a-user
.. _signup page: https://trello.com/signup

