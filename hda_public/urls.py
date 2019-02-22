from django.urls import path, register_converter
from hda_public.views import (
    HomeView,
    StateView,
    CountyView,
    HealthView,
    ChartView,
    SearchView,
    IndicatorOverviewCounty,
    IndicatorOverviewState,
)

# only successful method of import for this new view
from hda_public.views.location_selection import HealthStatePathView
from hda_public.converters import StateUSPSConverter, FIPS3Converter

# custom path converters to validate:
# - USPS 2-letter state codes:
register_converter(StateUSPSConverter, 'usps')
# - 3-digit FIPS codes.
register_converter(FIPS3Converter, 'fips3')

# we could acheive a prettier URL by slugifying the county names!
# https://stackoverflow.com/a/837835

urlpatterns = [
    # the home page:
    path('', HomeView.as_view(), name='home'),
    # a chart page that can show any counties given as a query parameter:
    path('chart/<int:indicator>', ChartView.as_view(), name='chart'),
    # location selection pages
    path('select/', StateView.as_view(), name='state'),
    path('select/<usps:short>', CountyView.as_view(), name='county'),
    path('select/<usps:short>/<fips3:fips>',
         HealthView.as_view(), name='metric'),
    path('select/indicator/<usps:short>/',
         HealthStatePathView.as_view(), name='selection_state_metric'),
    # search results page
    path('search/', SearchView.as_view(), name='search'),
    # overview pages for states and counties
    path('state/<usps:state>', IndicatorOverviewState.as_view()),
    path('county/<usps:state>/<fips3:county>', IndicatorOverviewCounty.as_view()),
]
