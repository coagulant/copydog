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

``TRELLO_TOKEN`` - your `consumer token <https://trello.com/docs/gettingstarted/index.html#getting-a-token-from-a-user>`_ to access Trello API

Obtain trello token for forever access r+w: https://trello.com/1/authorize?key=substitutewithyourapplicationkey&name=My+Application&expiration=never&response_type=token&scope=read,write

You also need redis server running with default configuration.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

