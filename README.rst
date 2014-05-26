Django Account Keeping
============

A reusable Django app for keeping track of transactions in your bank accounts.

Installation
------------

To get the latest stable release from PyPi

.. code-block:: bash

    pip install django-account-keeping

To get the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/bitmazk/django-account-keeping.git#egg=account_keeping

TODO: Describe further installation steps (edit / remove the examples below):

Add ``account_keeping`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'account_keeping',
    )

Add the ``account_keeping`` URLs to your ``urls.py``

.. code-block:: python

    urlpatterns = patterns('',
        ...
        url(r'^accounting/', include('account_keeping.urls')),
    )

Before your tags/filters are available in your templates, load them by using

.. code-block:: html

	{% load account_keeping_tags %}


Don't forget to migrate your database

.. code-block:: bash

    ./manage.py migrate account_keeping


Usage
-----

TODO: Describe usage or point to docs. Also describe available settings and
templatetags.


Contribute
----------

If you want to contribute to this project, please perform the following steps

.. code-block:: bash

    # Fork this repository
    # Clone your fork
    mkvirtualenv -p python2.7 django-account-keeping
    make develop

    git co -b feature_branch master
    # Implement your feature and tests
    git add . && git commit
    git push -u origin feature_branch
    # Send us a pull request for your feature branch
