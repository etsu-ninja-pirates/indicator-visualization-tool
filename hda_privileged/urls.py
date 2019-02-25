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
         name='dashboard1'),
    # creating new health indicators
    path('indicator/add/',
         login_required(views.HealthIndicatorCreate.as_view(), login_url='priv:login'),
         name='createIndicator'),
    # update an existing health indicator
    path('indicator/update/<int:post_pk>/',
         login_required(views.HealthIndicatorUpdate.as_view(),
                        login_url='priv:login'),
         name='updateIndicator'),
    # delete an existing health indicator
    path('indicator/delete/<int:post_pk>/',
         login_required(views.HealthIndicatorDelete.as_view(),
                        login_url='priv:login'),
         name='deleteIndicator'),
    # delete an existing dataset
    path('dataset/delete/<int:post_pk>/',
         login_required(views.DataSetDelete.as_view(),
                        login_url='priv:login'),
         name='deleteDataset'),
    # upload page
    path('upload/',
         login_required(views.UploadNewDataView.as_view(), login_url='priv:login'),
         name='uploadData'),
    # login/logout
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
