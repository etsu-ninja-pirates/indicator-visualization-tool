from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import HttpResponse
from hda_privileged.models import Data_Point
# from django.db.models import Count, Q
from django.http import JsonResponse
from django.core import serializers
import json


class ChartView(TemplateView):
    """ 
        This class will be used to display Json content that will be return
        from the char_data function 
    """
    template_name = 'hda_public/sample2.html'


    def get_chart(self, request): 
        chartdata = json.dumps([[pt.percentile, pt.value] for pt in Data_Point.objects.all()])
        return render(request, self.template_name, {'chartdata': chartdata})
        list_counties_data = list()
        list_values_data = list() 
        list_percentiles_data = list()

        for entry in datasets: 
            list_counties_data.append(entry['county_id'])
            # list_values_data.append(entry['vale'])
            list_percentiles_data.append(entry['percentile'])

        # value_series = {
        #     'name'  :  'Values',
        #     'data'  :  list_values_data, 
        #     'color' : 'green' 
        # }
        

        percentile_series = {
            'name' : 'Percentile', 
            'data' : list_percentiles_data 
        }

        chart = {
        'chart': {'type': 'column'},
        'title': {'text': 'Health Indicator'},
        'xAxis': {'Counties': list_counties_data},
        'series': [percentile_series]
         }

        dump = json.dumps(chart)

        # messages.error(request, 'An unexpected error occured.')
        return render(request, self.template_name,{'chart': dump})
  

class DashboardView(TemplateView):
    template_name = 'hda_public/dashboard.html'

    def get_view(self, request): 
        return render(request,self.template_name)


class TableView(TemplateView):
    template_name = 'hda_public/table.html'

    def get(self, request): 
        datasets = Data_Point.objects.all()
        args = {'datasets': datasets}
        return render(request,self.template_name, args)