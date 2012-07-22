Welcome to copydog's documentation!
===================================

To be done!

.. toctree::
   :maxdepth: 2

Launching tests
===============

To launch tests execute::

   nosetests

Note, that some tests make actual API requests, so you need to setup some env variables to make them pass:

``REDMINE_HOST`` - the host of your remdie instance

``REDMINE_API_KEY`` - your API key to access Redmine API

``TRELLO_API_KEY`` - the `API key <https://trello.com/1/appKey/generate>`_ of your Trello app

``TRELLO_TOKEN`` - your `consumer token <https://trello.com/docs/gettingstarted/index.html#getting-a-token-from-a-user>`_ to access Trello API ()

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

