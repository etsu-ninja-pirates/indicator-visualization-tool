import json

from django.views.generic import TemplateView

from hda_public.queries import mostRecentDataSetForIndicator
from hda_privileged.models import Health_Indicator, US_State


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
    context['state_id'] = state.short
    context['state_name'] = state.full
    context['indicator_id'] = indicator.id
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
