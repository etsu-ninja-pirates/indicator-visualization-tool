from django.urls import path, register_converter
from hda_public.views import (
    DashboardView,
    SingleCountyChartView,
    SingleStateChartView,
    TableView,
    StateView,
    CountyView,
    HealthView
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
    # the home page
    path('', DashboardView.as_view(), name='dashboard'),
    # displaying single charts:
    # highlighting a single county, identified as state + county + metric
    path('chart/<usps:state>/<fips3:county>/<int:indicator>', SingleCountyChartView.as_view(), name='chart'),
    # highlighting the counties in a state, identified as state + metric
    path('chart/<usps:state>/<int:indicator>', SingleStateChartView.as_view(), name='chart'),
    # old data table view
    path('table/', TableView.as_view(), name='table'),
    path('state/', StateView.as_view(), name='state'),
    path('state/<str:short>', CountyView.as_view(), name='county'),
    path('state/<str:short>/<fips3:fips>', HealthView.as_view(), name='metric'),
]
