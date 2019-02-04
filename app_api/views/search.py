from django.http import JsonResponse
from django.views import View

from django.db.models import F

from hda_privileged.models import US_State, US_County


def build_county_search_object(county):
    tokens = county.name.split(' ')
    tokens.append(county.state.short)
    tokens.append(county.state.full)
    display = f"{county.name}, {county.state.short}"
    return {
        'id': county.fips5,
        'name': county.name,
        'display': display,
        'tokens': tokens,
    }


class ObjectList(View):
    model = None
    id_field = ''
    name_field = ''

    def get(self, request):
        values = self.model.values(id=F(self.id_field), name=F(self.name_field))
        as_list = list(values.iterator())
        return JsonResponse({'values': as_list})


# TODO: make a static version of this! Load time is almost 3 seconds!
class CountyPrefetch(View):

    def get(self, request):
        all_of_them = US_County.objects.all().order_by('state', 'name')
        objects = [build_county_search_object(c) for c in all_of_them.iterator()]
        return JsonResponse(objects, safe=False)  # I want to serialize an array


class StatePrefetch(ObjectList):
    model = US_State
    id_field = 'short'
    name_field = 'full'


class Suggestions(View):

    def get(self, request, query=None):
        objects = []

        if query:
            matches = US_County.objects.filter(name__icontains=query).order_by('name')
            objects = [build_county_search_object(c) for c in matches.iterator()][:15]

        return JsonResponse(objects, safe=False)
