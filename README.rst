FedEx Day Voting Machine
========================

A Pyramid application that supports FedEx Day voting.

Getting Started
---------------

First, clone the code::

    $ git clone git@github.com:sixfeetup/fedexvoting.git

You will need a virtualenv set up::

    $ virtualenv -p python2.6 fedexvoting

Now set up a development environment::

    (fedexvoting)$ cd fedexvoting
    (fedexvoting)$ python setup.py develop

Then start up the paster server::

    (fedexvoting)$ paster serve development.ini --reload

Now you can access the site at `<http://127.0.0.1:6543>`_
