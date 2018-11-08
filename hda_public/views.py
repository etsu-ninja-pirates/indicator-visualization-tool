import json
from django.views.generic import TemplateView, ListView
from django.shortcuts import render

from hda_public.queries import (
    dataSetYearsForIndicator,
    dataSetForYear,
    mostRecentDataSetForIndicator
)
from hda_privileged.models import (
    Data_Point, US_State, US_County, Health_Indicator, Data_Set
)


# TODO: this has almost no error handling!
def build_chart_context(context, state_usps, indicator_id, county_fips=None):

    def transform_point(pt):
        return {
            'x': pt.rank * 100,
            'y': pt.value,
            'name': pt.county.name,
        }

    state = US_State.objects.get(short=state_usps)
    indicator = Health_Indicator.objects.get(id=indicator_id)

    dataset = mostRecentDataSetForIndicator(indicator_id)

    # add labels
    context['state_name'] = state.full
    context['indicator_name'] = indicator.name

    # add percentile values for backing spline curve
    percentiles = dataset.percentiles.all().order_by('rank')
    percentile_data = json.dumps([(p.rank * 100, p.value) for p in percentiles])
    context['data_percentiles'] = percentile_data

    # add the actual data series - the selected counties
    # eventually this could be a list, for now either they chose one or they didn't
    state_points = dataset.data_points.filter(county__state__short=state_usps)
    # if they selected a particular county, filter down to just a single element
    if county_fips is not None:
        state_points = state_points.filter(county__fips=county_fips)
        county = state.counties.get(fips=county_fips)
        context['county_name'] = county.name

    value_data = json.dumps([transform_point(pt) for pt in state_points])
    context['data_series'] = value_data

    return context


class SingleStateChartView(TemplateView):
    """ Our single-chart pages will highlight either a single county, or
    the counties in a state. Rather than have one class handle both these cases,
    we'll use a different view for each to make the logic simpler. This class
    displays the counties in on state for a single indicator/metric.
    """
    template_name = 'hda_public/chart.html'

    def get_context_data(self, **kwargs):

        # call superclass to get a base context dictionary
        context = super().get_context_data(**kwargs)

        # we have two keyword parameters:
        # - state (a USPS short code)
        # - indicator (an int)
        # they should already be ready to match against our model, and they should both be present,
        # since this class is only used with a single URL pattern
        selected_state = self.kwargs.get('state', None)
        selected_metric = self.kwargs.get('indicator', None)

        if selected_metric is None or selected_state is None:
            raise TypeError('SingleStateChartView needs state and metric URL parameters!')

        # fill the context with the data needed to render a chart
        populated_context = build_chart_context(context, selected_state, selected_metric)

        # return the context to the template for rendering
        return populated_context


class SingleCountyChartView(TemplateView):
    """ This class renders a page with a single chart that shows a single county for
    a single health metric. This is very similar to the StateChartView, but it keeps
    the logic slightly less branch-y to have two separate views here.
    """
    template_name = 'hda_public/chart.html'

    def get_context_data(self, **kwargs):

        # call super to get the base context
        context = super().get_context_data(**kwargs)

        selected_state = self.kwargs.get('state', None)
        selected_county = self.kwargs.get('county', None)
        selected_metric = self.kwargs.get('indicator', None)

        if selected_metric is None or\
                selected_state is None or\
                selected_county is None:
            raise TypeError('SingleCountyChartView needs state, county, and metric URL parameters!')

        # fill the context with the data needed to render a chart
        populated_context = build_chart_context(
            context,
            selected_state,
            selected_metric,
            county_fips=selected_county
        )

        return populated_context


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


class StateView(ListView):
    template_name = 'hda_public/state.html'
    paginate_by = '15'
    model = US_State
    context_object_name = "states"

    def get_queryset(self):
        states = US_State.objects.all()
        return states

    def get_context_data(self, **kwargs):
        context = super(StateView, self).get_context_data(**kwargs)
        context['range'] = range(context['paginator'].num_pages)
        return context


class CountyView(ListView):
    template_name = 'hda_public/county.html'
    paginate_by = '15'
    model = US_County
    context_object_name = "counties"

    def get_context_data(self, **kwargs):
        context = super(CountyView, self).get_context_data(**kwargs)
        context['range'] = range(context['paginator'].num_pages)
        state_short_name = self.kwargs.get('short', None)

        if state_short_name is not None:
            context['state'] = US_State.objects.filter(short=state_short_name).first().full
            context['state_short_name'] = state_short_name

        return context

    def get_queryset(self):
        state_short_name = self.kwargs.get('short', None)
        counties = None

        if state_short_name is not None:
            associated_state = US_State.objects.filter(short=state_short_name).first()
            counties = US_County.objects.filter(state=associated_state)

        return counties


class HealthView(TemplateView):
    template_name = 'hda_public/health_indicator.html'

    #to make the county unique in the list
    def get(self, request, **kwargs):
        fips = self.kwargs.get('fips', None)
        state_short = self.kwargs.get('state_id', None)
        args = None

        # if fips is not None and state_short is not None:
        # state = US_State.objects.filter(short=state_short).first()
        # data_points = Data_Point.objects.filter(county__fips=fips)
        # health_indicators = data_points.all()
        # args = {'indicators': health_indicators}

        if fips is not None and state_short is not None:
            state = US_County.objects.filter(state=state_short).first()
            #county_dp = Data_Point.objects.filter(county=US_County.state, data_set=Data_Set.indicator, data_set__year=Data_Set.year)
            #county_dp_ds = Data_Point.objects.filter(dataset_id=Data_Set)
            #county_metric = Data_Set.objects.filter(indicator_id=Data_Set.indicator)
            #indicators = Health_Indicator.objects.filter(indicator_id= Health_Indicator.id)
            test=Data_Point.objects.filter(county=US_County.state,data_set=Data_Set.indicator) and Health_Indicator.objects.filter(name=Health_Indicator.name, data_sets=Health_Indicator.data_sets)

            return test

        return render(request, self.template_name, args)
