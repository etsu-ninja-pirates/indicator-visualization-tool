from django.urls import path
from hda_public.views import DashboardView, ChartView, TableView, TestView, TestTemplateView
from . import views

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('chart/', ChartView.as_view(), name='chart-data'),
    path('table/', TableView.as_view(), name='table'),
    path('test/<int:year>', TestTemplateView.as_view()),
    path('test/', TestTemplateView.as_view()),
]
