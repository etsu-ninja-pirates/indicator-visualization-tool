import json

from django.views.generic import TemplateView
from django.shortcuts import render

from hda_public.queries import dataSetYearsForIndicator, dataSetForYear
from hda_privileged.models import Data_Point


class ChartView(TemplateView):
    """
        This class will be used to display Json content that will be return
        from the char_data function
    """
    template_name = 'hda_public/chart.html'

    # things that need to go into the context:
    # 1. Is a year selected? (If not, we won't show a chart because we can't query data)
    # 2. The selectable years
    # 3. Series data for the chart, if a year was selected
    def get_context_data(self, **kwargs):
        # helper function to transform data points into plot series data
        def transform(pt):
            return {
                'x': pt.rank * 100,
                'y': pt.value,
                'name': pt.county.name,
            }

        # call super to get the base context
        context = super().get_context_data(**kwargs)

        # did the URL specify a year?
        selected_year = self.kwargs.get('year', None)
        context['selected_year'] = selected_year

        # query the model for the available years (matching data sets we have)
        # use default indicator name for demo
        year_options = dataSetYearsForIndicator()
        context['available_years'] = year_options

        if selected_year is not None:
            data_set = dataSetForYear(selected_year)
            if data_set is not None:
                # in this branch, the user selected a year and we successfully
                # retrieved the data set for that year
                points = data_set.data_points.filter(county__state__short='TN')
                percentiles = data_set.percentiles.all().order_by('rank')
                
                value_data = json.dumps([transform(pt) for pt in points])
                percentile_data = json.dumps([(p.rank * 100, p.value) for p in percentiles])
                
                context['data_series'] = value_data
                context['data_percentiles'] = percentile_data
            else:
                # in this branch, they selected a year, but we couldn't find that data set (?!)
                # ...what to do? we'll reset the selected year to None - the page will render 
                # like they did not select a year
                context['selected_year'] = None

        # return the context dictionary to the template can use it
        return context


class DashboardView(TemplateView):
    template_name = 'hda_public/dashboard.html'

    def get_view(self, request):
        return render(request, self.template_name)


class TableView(TemplateView):
    template_name = 'hda_public/table.html'

    def get(self, request):
        datasets = Data_Point.objects.all()
        args = {'datasets': datasets}
        return render(request, self.template_name, args)