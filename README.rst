Django Account Keeping
======================

A reusable Django app for keeping track of transactions in your bank accounts.

Installation
------------

To get the latest stable release from PyPi

.. code-block:: bash

    pip install django-account-keeping

To get the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/bitmazk/django-account-keeping.git#egg=account_keeping


Add ``account_keeping`` and ``currency_history`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'account_keeping',
        'currency_history',
    )

Add the ``account_keeping`` URLs to your ``urls.py``

.. code-block:: python

    urlpatterns = patterns('',
        ...
        url(r'^accounting/', include('account_keeping.urls')),
    )

Don't forget to migrate your database

.. code-block:: bash

    ./manage.py migrate account_keeping
    ./manage.py migrate currency_history


Usage
-----

Configure currency history app
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Follow the instructions at: https://github.com/bitmazk/django-currency-history

Make sure you add all needed currencies first. Second, define the wanted rates.
Then make sure to get the latest rate history and add it by yourself.

Add Account objects
^^^^^^^^^^^^^^^^^^^

Next you need to create your accounts. Note that the field `total_amount` is
currently not used. It might eventually be used in the future for performance
optimisations but at the moment it seems that computing the totals on the
fly is fast enough.

Import data from Money Manager Ex
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you were using Money Manage Ex, you can export your data into a .csv file
and then import it into this app::

    ./manage.py importer_mmex -f filename.csv -c EUR -t 19 -a account-slug

The parameter `-t` (VAT) is optional. If omitted, it is assumed that there is
no VAT for the transactions in this account.

IMPORTANT: Money Manager Ex has a transaction type `Transfer` but unfortunately
in the `.csv` format the information of the source and destination accounts is
lost. Here is a workaround: First you go through all your transactions in
Money Manager Ex and those that have an incoming transfer (a deposit), you mark
by adding some unique text to the description. Then you export the `.csv` and
edit it in an editor. You search for your unique string and for those rows you
change the transaction type from `Transfer` to `TransferDeposit`.

Money Manager Ex does not have the notion of invoices, it only has
transactions. When importing the data, this app will simply generate a dummy
invoice for each transaction. Unfortunately, you have to go through all
transactions manually and change the incoive date.

Creating transactions with sub-transactions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes a customer will pay several invoices within one transaction. For this
case you should do the following:

1. Create the transaction that has appeared on your bank account as usual
2. For each invoice that has been paid, create a transaction that has the
   first transaction as a parent and of course create an invoice that is tied
   to it's transaction.

Settings
^^^^^^^^

BASE_CURRENCY
*************

Default: 'EUR'

Define a default currency. All time statistics and summaries are displayed
using this setting.

Currently available views
^^^^^^^^^^^^^^^^^^^^^^^^^

Alltime overview
****************

URL: ../all/

Shows all transactions for all accounts, all time totals and outstanding
invoices.

Year overview
*************

URL: ../YYYY/

Shows a table with total expenses, income, profit for each month of the year.
Also shows how many new invoices have been sent to customers each month and
how many invoices have been outstanding for each month.

Shows the total bank balance for each month (at the end of each month) and
total equity (bank balance + outstanding invoices).

Month overview
**************

URL: ../YYYY/MM/

Shows all transactions for all accounts for the given month.

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
