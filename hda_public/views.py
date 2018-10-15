from django.views.generic import TemplateView
from django.shortcuts import render
from hda_privileged.models import Data_Point, Data_Set
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
        
        kpi_name = 'Obisity'
        
        # function call that returns all the years based on the KPI that is passed to it  
        years = showallYears(kpi_name)

        # for demo purposes, grab the first data set
        ds = Data_Set.objects.first()
        # filter for the data points from counties in New York state
        points = ds.data_points.filter(county__state__short='NY')
        # pts = ds.data_points.all()
        # transform the points into a list of objects for Highcharts
        chartdata = json.dumps([trans(pt) for pt in points])

        return render(request, self.template_name, { 'chartdata': chartdata})


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

# This method will be used to test the return of all the data sets poining to a particular year 
def showallYears(kpi_name):
    """ This function takes in a KPI name then returns all the years liked to it """
    ds = Data_Set.objects.all().filter(indicator__name = kpi_name).order_by('year')
    years = [i.year for i in ds]
    return years