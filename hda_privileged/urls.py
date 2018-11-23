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
    path('metric/create/', views.create_metric, name='create_metric'),
    path('metric/', views.manage_metrics, name='manage_metrics'),
    # upload page
    path('upload/', login_required(views.UploadNewDataView.as_view(), login_url='priv:login'), name='upload_metric'),
    # login/logout
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
