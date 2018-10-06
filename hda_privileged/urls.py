from django.urls import path

from . import views

urlpatterns = [
    path('sample/', views.sampleNavBar, name='sample'),
    path('login/', views.user_login, name='login'),
    path('metric/', views.manage_metrics, name='manage_metrics'),
    path('metric/create/', views.create_metric, name='create_metric'),
    path('upload/', views.upload_metric, name='upload_metric'),
]
