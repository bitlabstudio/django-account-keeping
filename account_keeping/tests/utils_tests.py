"""Tests for the utils of the account_keeping app."""
import datetime

from django.test import TestCase

from .. import utils


class GetDateTestCase(TestCase):
    """Tests for the ``get_date`` function."""
    longMessage = True

    def test_function(self):
        self.assertEqual(utils.get_date('2014-01-01'),
                         datetime.datetime(2014, 1, 1))
        self.assertEqual(utils.get_date(1), 1)


class GetMonthsOfYearTestCase(TestCase):
    """Tests for the ``get_months_of_year`` function."""
    longMessage = True

    def test_function(self):
        self.assertEqual(
            utils.get_months_of_year(datetime.datetime.now().year - 1), 12)
        self.assertEqual(
            utils.get_months_of_year(datetime.datetime.now().year + 1), 1)
        self.assertEqual(
            utils.get_months_of_year(datetime.datetime.now().year),
            datetime.datetime.now().month)
