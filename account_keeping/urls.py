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

    url(r'current-year/$',
        views.CurrentYearRedirectView.as_view(),
        name='account_keeping_current_year'),

    url(r'current-month/$',
        views.CurrentMonthRedirectView.as_view(),
        name='account_keeping_current_month'),

    url(r'$',
        views.IndexView.as_view(),
        name='account_keeping_index'),
)
