"""Tests for the template tags of the account_keeping app."""
from django.test import TestCase

from ..templatetags import account_keeping_tags


class CurrencyTestCase(TestCase):
    """Tests for the ``currency`` filter."""
    longMessage = True

    def test_tag(self):
        self.assertEqual(
            account_keeping_tags.currency('1.1111100'), 'EUR 1.11')


class GetBranchesTestCase(TestCase):
    """Tests for the ``get_branches`` filter."""
    longMessage = True

    def test_tag(self):
        self.assertEqual(account_keeping_tags.get_branches().count(), 1)
