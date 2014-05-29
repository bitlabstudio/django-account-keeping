"""URLs for the account_keeping app."""
from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns(
    '',
    url(r'all/$',
        views.AllTimeView.as_view(),
        name='account_keeping_all'),

    url(r'(?P<year>\d+)/(?P<month>\d+)/$',
        views.MonthView.as_view(),
        name='account_keeping_month'),

    url(r'(?P<year>\d+)/$',
        views.YearOverviewView.as_view(),
        name='account_keeping_year'),
)
