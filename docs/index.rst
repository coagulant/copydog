Copydog
-------

Copydog converts issues between Redmine_ and Trello_ on the fly.
It's a small third-party daemon, monitoring changes in both systems and keeping
them in sync as much as possible.

You might find this tool useful after reading `How it works`_.

.. warning::
    Copydog is in active development, it's not ready for production yet.
    However, please, feel free to experiment/test and use the code.

.. _Redmine: http://redmine.org/
.. _Trello: http://trello.com/

Installation
============

Git clone the repo https://github.com/coagulant/copydog.git
You also need a Redis_ instance to store intermediate results of syncronization.
For best experience please install Pandoc_ to convert issues descriptions
between Markdown and Textile.

Copydog is not yet available as package, so please install dependencies
manualy (they're listed in setup.py).

Copydog runs on python 2.6-2.7 only. Python 3 support is planned in future releases.

Configuration
=============

For copydog to work you need both Trello and Redmine accounts.

Trello
^^^^^^
If you don't have an account, head over to `signup page`_ and register.
After that you need to obtain you API key and user token.

    * Generate_ the API key for your application (need to be logged in).

    * A token grants permissions (read, write or both) to one application
      for a specific user. To get a token for yourself, visit `the docs`_.

.. note::

    Obtain Trello token granting forever read and write access::

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
Here is how config file might look like:

.. code-block:: yaml

    clients:
      redmine:
        host: http://redmine.org
          api_key: ac7785e2c593ad6d7f539f2f90be26ba0851d18a
          project_id: playground
          write: 1
        trello:
          api_key: 9e90d281ed678b56b041871c3651ee2d
          token: e80a1138e0b5ea08d506fcabe6c17196542af7ee684c6c24b6f5b79
          board_id: 4fe889e4c23b476f4a189ca5
          write: 1
    storage:
      redis:
        host: localhost
        port: 6379
        db: 0
        password:None
    copydog:
      pandoc: '/usr/bin/pandoc'
      beat: 60

Note, how config is separated into sections: ``clients``, ``storage`` and ``copydog``.
First one is required, other are completely optional.
Clients have to be ``redmine`` and ``trello``, with following attributes:

* ``redmine``
    * ``host`` - the host of your redmine instance
    * ``api_key`` - your API key to access Redmine API
* ``trello``
    * ``api_key`` - the API key  of your Trello app
    * ``token`` - your consumer token to access Trello API

This keys can be obtained via browser, please read above sections for both redmine and trello.

.. note::
    Copydog supports syncing one redmine project with one trello board at a time,
    so you need to specify ``project_id`` (string slug or integer) and ``board_id`` (string id).

Storage config might be completely omitted if you're using default Redis connection.
Write flag allows copydog to modify contents on a client, set it to 0
to disable sync writes to either redmine or trello.

You can optionally provide ``tracker_id`` and/or ``fixed_version_id`` in redmine
section to limit the number of issues being synced.

.. note::
    While Redmine can handle thousands of issues painlessly, Trello is simply not
    suited for that amount of cards per board. I recommend using ``tracker_id`` or
    ``fixed_version_id`` filters to make better use of Trello.

By default copydog polls servers every minute. Is not a big burden for external
APIs and sufficient to stay up to date. If it doesn't suite your needs, feel free to change
the beat frequency under ``copydog`` section in config (it's called ``beat`` and is measured in seconds between
polls.


Running copydog
===============
To launch the app::

    python runner.py --config=<path_to_your_yaml_config>

Copydog will start monitoring `new` changes in both services and mirror them accordingly.
If you wish to sync all existing issues/card, use ``--fullsync`` option::

    python runner.py --fullsync --config=<path_to_your_yaml_config>

Deamon
^^^^^^
If you're not developing copydog it's useful to run it as daemon process.
To daemonize copydog, run it with a ``start`` argument::

    python runner.py start --config=<path_to_your_yaml_config>

Copydog will run in background unless you stop it::

    python runner.py stop --config=<path_to_your_yaml_config>

How it works
============
Copydog polls both Redmine and Trello in turns, converting data from one service to
the other. It queries first service for issues, updated since the last read and saves
their identifiers and timestamps in storage. If there are any, they're converted_ into
sister service type. Copydog tracks both new issues/cards and updates of existing ones
by storing references between issues and cards. Trello cards are created with comments,
featuring urls to corresponding redmine issues.

.. _converted:

Fields mapping
^^^^^^^^^^^^^^
Copydog tries to be smart when transferring cards to issues and vice versa.
Redmine statuses are associated with Trello lists and are mapped by exact name match,
so make sure you have same set of Statuses and Lists in your project and your board.
Assigned members are linked by username or full name as a fallback.

============   ==========  =========
Redmine        Trello      Comment
============   ==========  =========
subject        name
description    desc        Text is converted with `pandoc`_, if available. See :ref:`markup-conversion`
assigned_to    idMembers   Redmine doesn't support multiple assignees, the first one is taken.
status_id      idList      Copydog maps each status to list by name
project_id     board_id    One board is synced with one project only
due_date       due
============   ==========  =========

Other data like priorities, comments, labels are not synced.

.. _markup-conversion:

Markup conversion
^^^^^^^^^^^^^^^^^
Copydog tries to use Pandoc_ tool to convert issue text between between services.
For example, Trello understands Markdown_ and Redmine uses Textile_.
If you dont' have pandoc installed, issues texts would be transferered as is.
This not always nice looking, so I advice you to install pandoc anyway.

You can provide a path to pandoc binary in config under ``copydog`` section.

.. code-block:: yaml

    copydog:
      pandoc: '/usr/bin/pandoc'

.. _Markdown: http://daringfireball.net/projects/markdown/
.. _Textile: http://textile.thresholdstate.com/

Storage
^^^^^^^
Copydog needs intermediate storage to save references between issues in Redmine and Trello.
It also stores when items were last updated to make sure we're not going to
sync issues back and forth forever. Copydog remembers time of last sync, so it will resume
its work from the same spot.

Redis database is used for storing this data. If you wish to use another utility, you should
write your own Storage backend.

Development
===========

Copydog is developed and maintained by `Baryshev Ilya`_.
Feel free to submit `issues`_ or comments at development `Trello board`_.

.. _Baryshev Ilya: https://github.com/coagulant
.. _issues: https://github.com/coagulant/copydog
.. _Trello board: https://trello.com/board/copydog/501954bc8c03157b50d6f7ef

Launching tests
^^^^^^^^^^^^^^^

To launch tests execute::

   nosetests

Some tests make actual API read requests, but they're disabled by default, to run them use::

   nosetests -c all

These tests will pass if you have following env variables set:

* ``COPYDOG_REDMINE_HOST`` - the host of your redmine instance
* ``COPYDOG_REDMINE_API_KEY`` - your API key to access Redmine API
* ``COPYDOG_TRELLO_API_KEY`` - the API key  of your Trello app
* ``COPYDOG_TRELLO_TOKEN`` - your consumer token to access Trello API

REST API references
^^^^^^^^^^^^^^^^^^^

* `Redmine  API docs <http://www.redmine.org/projects/redmine/wiki/Rest_api>`_
* `Trello API overview <https://trello.com/docs/index.html>`_
* `Trello API docs <https://trello.com/docs/api/>`_


Changelog
=========
ver 0.1 (TBA)
^^^^^^^^^^^^^
* Initial release


.. _Redis: http://redis.io/
.. _generate: https://trello.com/1/appKey/generate
.. _the docs: https://trello.com/docs/gettingstarted/index.html#getting-a-token-from-a-user
.. _signup page: https://trello.com/signup
.. _pandoc: http://johnmacfarlane.net/pandoc


