from django.urls import path
from hda_privileged.views import PrivDashboardView
from . import views

urlpatterns = [
    path('home/', PrivDashboardView.as_view(), name='privdashboard'),   
    path('login/', views.user_login, name='login'),
    path('metric/', views.manage_metrics, name='manage_metrics'),
    path('metric/create/', views.create_metric, name='create_metric'),
    path('upload/', views.UploadNewDataView.as_view(), name='upload_metric'),
]
