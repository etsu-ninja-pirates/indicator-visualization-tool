from django.conf.urls import url


from . import views

urlpatterns = [
        url('^$', views.user_login, name='login'),
        url('dashboard/', views.dashboard,  name='dashboard'),

]