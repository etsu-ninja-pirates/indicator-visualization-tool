from django.urls import path
from hda_public.views import DashboardView, ChartView, TableView
from . import views

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('chart/', ChartView.as_view(), name='chart-data'),
    path('table/', TableView.as_view(), name='table')
]