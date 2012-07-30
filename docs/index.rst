Copydog
-------

Copydog seamlessly copies issues from Redmine_ to Trello_ and vice versa.
It's a small daemon, monitoring changes in both systems and keeping
them in sync as much as possible.

.. toctree::
    index


Installation
============

Git clone the repo https://github.com/futurecolors/copydog.git
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

Storage config might be completely ommited if you're using default Redis connection.


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

