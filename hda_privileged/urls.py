from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('metric/', views.manage_metrics, name='manage_metrics'),
    path('metric/create/', views.create_metric, name='create_metric'),
]
