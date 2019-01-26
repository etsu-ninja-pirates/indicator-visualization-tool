from django.urls import path, register_converter
from hda_public.views import (
    HomeView,
    SingleCountyChartView,
    SingleStateChartView,
    StateView,
    CountyView,
    HealthView,
    ChartView,
)
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
    # displaying single charts:
    # highlighting a single county, identified as state + county + metric
    path('chart/<usps:state>/<fips3:county>/<int:indicator>', SingleCountyChartView.as_view(), name='chart'),
    # highlighting the counties in a state, identified as state + metric
    path('chart/<usps:state>/<int:indicator>', SingleStateChartView.as_view(), name='chart'),
    # location selection pages
    path('state/', StateView.as_view(), name='state'),
    path('state/<usps:short>', CountyView.as_view(), name='county'),
    path('state/<usps:short>/<fips3:fips>', HealthView.as_view(), name='metric'),
]
