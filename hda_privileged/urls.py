from django.urls import path
from django.contrib.auth.decorators import login_required
from hda_privileged.views import PrivDashboardView, logout_view
from . import views

app_name = 'priv'
urlpatterns = [
    path('home/', views.PrivDashboardView.as_view(), name='privdashboard'),
    path('login/', views.user_login, name='login'),
    path('metric/', views.manage_metrics, name='manage_metrics'),
    path('metric/create/', views.create_metric, name='create_metric'),

    path('upload/', login_required(views.UploadNewDataView.as_view(), login_url='priv:login'), name='upload_metric'),
    path('logout', views.logout_view, name='logout'),
]
