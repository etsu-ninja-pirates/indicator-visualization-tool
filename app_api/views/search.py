from django.http import JsonResponse
from django.views import View

from django.db.models import F

from hda_privileged.models import US_State, US_County

from app_api.util import search


class ObjectList(View):
    model = None
    id_field = ''
    name_field = ''

    def get(self, request):
        values = self.model.values(id=F(self.id_field), name=F(self.name_field))
        as_list = list(values.iterator())
        return JsonResponse({'values': as_list})


class StatePrefetch(ObjectList):
    model = US_State
    id_field = 'short'
    name_field = 'full'


class Suggestions(View):
    '''
    Given some query, returns a JSON list of objects that might match that query.
    This is used by Bloodhound.js if its local object store does not provide enough
    results for what the user is typing, so the JSON objects use the same format as
    the Bloodhound prefetch data (see also management/commands/generate_prefetch_data.py)
    '''
    def get(self, request, query=None):
        objects = []

        if query:
            matches = US_County.objects.filter(name__icontains=query).order_by('name')
            objects = [search.datum_for_county(c) for c in matches.iterator()][:15]

        return JsonResponse(objects, safe=False)
