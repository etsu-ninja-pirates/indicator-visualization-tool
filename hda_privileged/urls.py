from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'priv'
urlpatterns = [
    # home/dashboard
    path('home/<int:indicator>/',
         login_required(views.PrivDashboardView.as_view(), login_url='priv:login'),
         name='dashboardselected'),
    path('home/',
         login_required(views.PrivDashboardView.as_view(), login_url='priv:login'),
         name='privdashboard'),
    # unused health indicator crud URLs
    path('metric/create/',
         login_required(views.create_metric, login_url='priv:login'),
         name='create_metric'),
    path('metric/',
         login_required(views.manage_metrics, login_url='priv:login'),
         name='manage_metrics'),
    # upload page
    path('upload/',
         login_required(views.UploadNewDataView.as_view(), login_url='priv:login'),
        name='upload_metric'),
    # login/logout
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
