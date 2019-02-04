from django.urls import path

import app_api.views.county as county
import app_api.views.state as state


app_name = 'api'
urlpatterns = [
    path('county/list/', county.ListAll.as_view()),
    path('state/list/', state.ListAll.as_view()),
]