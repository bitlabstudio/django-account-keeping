"""Utility functions for the account_keeping app."""

from django.utils.timezone import datetime, now


def get_date(value):
    """
    Returns the given field as a DateTime object.

    This is necessary because Postgres and SQLite return different values
    for datetime columns (DateTime vs. string).

    """
    if isinstance(value, basestring):
        return datetime.strptime(value, '%Y-%m-%d')
    return value


def get_months_of_year(year):
    """
    Returns the number of months that have already passed in the given year.

    This is useful for calculating averages on the year view. For past years,
    we should divide by 12, but for the current year, we should divide by
    the current month.

    """
    current_year = now().year
    if year == current_year:
        return now().month
    if year > current_year:
        return 1
    if year < current_year:
        return 12
