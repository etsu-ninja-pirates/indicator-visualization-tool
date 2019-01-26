# this just makes it easier to directly access classes when more than one is in a file
# externally, this lets us say
# 'from views import StateView'
# instead of
# 'from views.location_selection import StateView'
# see https://stackoverflow.com/a/26868297/5111071

# flake8: noqa
from .chartview import ChartView
from .homeview import HomeView
from .legacy_chart_views import SingleCountyChartView, SingleStateChartView
from .location_selection import StateView, CountyView, HealthView
