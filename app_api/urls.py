from django.urls import path

import app_api.views.county as county
import app_api.views.state as state

from app_api.views.search import CountyPrefetch, StatePrefetch, Suggestions


app_name = 'api'
urlpatterns = [
    # entities
    path('county/list/', county.ListAll.as_view()),
    path('state/list/', state.ListAll.as_view()),
    # search typeahead prefetch
    path('search/prefetch/county/', CountyPrefetch.as_view(), name='search_county_prefetch'),
    path('search/prefetch/state/', StatePrefetch.as_view(), name='search_state_prefetch'),
    # search suggestions
    path('search/suggestions/<str:query>/', Suggestions.as_view(), name='search_suggestions')

]