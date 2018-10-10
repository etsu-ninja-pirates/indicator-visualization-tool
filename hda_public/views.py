from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import render
from hda_privileged.models import Data_Point, Data_Set
import json


# Example of using URL parameter in a class-based view subclassing "django.views.generic.base.View"
# The "get" method becomes equivalent to a function-based view: it is called with the URL
# parameter as a keyword argument, so the parameter needs to be declared as part of the
# function signature for "get".
# https://docs.djangoproject.com/en/2.0/ref/class-based-views/base/#view
#
# (We *can* access self.kwargs here, but "get" is called with the parameter and Python will crash
# if you call a function with an undeclared keyword parameter.)
class TestView(View):
    def get(self, request, year=None):
        return render(request, 'hda_public/dashboard.html', {'year': year})

# Example of using URL parameter in a class based view subclassing "django.views.generic.base.TemplateView"
# TemplateView is intended to abstract over the HTTP methods, and allows you to override "get_context_data"
# to determine the context that gets passed to the template.
# https://docs.djangoproject.com/en/2.0/ref/class-based-views/base/#templateview
#
# Whenever class-based views are called Django populates the properties `self.request`, `self.args`, and
# `self.kwargs` - we can pull URL parameters out of self.args (positional) and self.kwargs (keyword),
# and use them to add to the context object sent to the template.
# https://docs.djangoproject.com/en/2.1/topics/class-based-views/generic-display/#dynamic-filtering
class TestTemplateView(TemplateView):
    template_name = 'hda_public/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['year'] = self.kwargs.get('year', None)
        return context


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

        return render(request, self.template_name, { 'chartdata': chartdata, 'years': years})


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