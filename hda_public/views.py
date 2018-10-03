from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import HttpResponse
from hda_privileged.models import Data_Point, Data_Set
# from django.db.models import Count, Q
from django.http import JsonResponse
from django.core import serializers
import json


class ChartView(TemplateView):
    """
        This class will be used to display Json content that will be return
        from the char_data function
    """
    template_name = 'hda_public/chart.html'


    def get(self, request):
        # this ne doesn't plot even though the data is delivered - is it because th object keys end up quoted?
        def trans(pt):
            return {
                'x': pt.percentile * 100,
                'y': pt.value * 100,
                'name': pt.county.name,
            }

        # for demo purposes, grab the first data set
        ds = Data_Set.objects.first()
        # filter for the data points from counties in New York state
        points = ds.data_points.filter(county__state__short='NY')
        # transform the points into a list of objects for Highcharts
        chartdata = json.dumps([trans(pt) for pt in points])

        return render(request, self.template_name, { 'chartdata': chartdata })


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
