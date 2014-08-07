"""Tests for the utils of the account_keeping app."""
import datetime

from django.test import TestCase

from .. import utils


class GetDateTestCase(TestCase):
    """Tests for the ``get_date`` function."""
    longMessage = True

    def test_function(self):
        result = utils.get_date('2014-01-01')
        self.assertEqual(result, datetime.datetime(2014, 01, 01))
