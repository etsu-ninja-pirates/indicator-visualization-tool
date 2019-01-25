import json
from django.contrib import messages
from django.views.generic import TemplateView, ListView
from django.shortcuts import render

from hda_public.queries import (
    dataSetYearsForIndicator,
    dataSetForYear,
    mostRecentDataSetForIndicator
)
from hda_privileged.models import (
    Data_Point, US_State, US_County, Health_Indicator
)


class ChartView(TemplateView):
    '''
    Works with URLs of the following shape:
    - a keyword path parameter called 'indicator', which is an integer Health_Indicator ID
    - one of two query strings to specify what counties to display:
       + `?state=<USPS>`, where <USPS> is a 2-letter USPS postal code for a state
       + `?county=<FIPS_LIST>`, where <FIPS_LIST> is comma-separated list of *5-digit* FIPs codes

    Examples:
    * /chart/3?state=TN
    * /chart/3?county=01002,01005,01007

    The view will retrieve the most recent data set for the requested Health Indicator, if one
    exists. It will add a data series for HighCharts containing the data points from that data
    set for each of the requested counties; either all the counties in the requested state, or
    each county matching one of the requested 5-digit FIPs codes.

    Each stage of context processing is broken into a separate function. Each function takes in
    the context dictionary and additional state from the previous stage, augments the context
    object in some way, and returns the updated context, a flag indicating whether to halt
    processing, and any additional state the next stage will require. The stages are listed in
    order and executed in the `decorate_context` function.

    See `chart_context_pipeline.txt` for a graph of the stages, their I/O, and possible warnings
    and errors generated at each stage.
    '''

    template_name = 'hda_public/chart.html'

    # 1: were we given an indicator ID, and does that indicator exist?
    # if so, add it to the context, and return it as an extra value so
    # functions further down the pipe can use it without knowing
    # what dictionary key we used
    # (either way is fragile, so not sure what the difference really is)
    def indicator_decorator(self, context):
        '''
        Stage 1 of context processsing.

        Check for an indicator ID as a *keyword argument* in the URL.
        Will throw a TypeError instead of rendering the page if the argument is not available,
        because this would be a programming error (the view would have to be paired with an incorrect
        URL pattern in URLconf).

        In case of error, adds an error message on the 'error' key of the context object, adds a message
        to the messages framework at the 'error' level, and stops additional stages.

        Inputs: context
        Outputs: context, Health Indicator instance
        Errors: No health indicator matched the ID we were given
        '''
        indicator_id = self.kwargs.get('indicator', None)

        if indicator_id is None:
            raise TypeError("ChartView needa a health indicator ID, but none was given")

        try:
            indicator = Health_Indicator.objects.get(id=indicator_id)
            context['indicator'] = indicator
            return (context, True, indicator)

        except Health_Indicator.DoesNotExist:
            msg = f"There is no health indicator matching the selected ID ({indicator_id})"
            context['error'] = msg
            messages.error(self.request, msg)
            return (context, False)

    # 2: does that indicator have a data set?
    # if it does, don't add the whole thing to the context, just pass it down the pipe
    # FIXME: this always gets the most recent data set, which may not include the county the user requested
    # (they may have asked for a ocunty that is only included in an older data set for the same indicator!)
    def data_set_decorator(self, context, indicator):
        '''
        Stage 2 of context processing

        Given an indicator, queries the most recent data set for that indicator and
        passes it along to the next stage.

        If no indicator exists, adds an error message to the context object and messages
        framework, and stops further stages.

        Inputs: context, Health Indicator instance
        Outputs: context, Data Set instance
        Errors: no data set exists for the given indicator
        '''
        dataset = indicator.data_sets.order_by('-source_document__uploaded_at').first()

        if dataset is None:
            msg = f"No data exists for indicator {indicator.id}"
            context['error'] = msg
            messages.error(self.request, msg)
            return (context, False)
        else:
            return (context, True, dataset)

    # 3. add the percentiles spline curve to the context
    def percentiles_decorator(self, context, data_set):
        '''
        Context processing stage 3:
        Given a data set object, serializes the percentiles for that data set in a format
        HighCharts likes and adds the serialized data to the context object for display.

        Input: context, data set
        Output: context, data_set
        Errors: none
        '''
        percentiles = data_set.percentiles.all().order_by('rank')
        percentiles_json = json.dumps([(p.rank * 100, p.value) for p in percentiles])
        context['data_percentiles'] = percentiles_json
        return (context, True, data_set)

    def try_get_state(self, usps):
        '''
        Given a string, interpret the string as a USPS code for a US_State
        and try to query that state from the database.
        Returns none if the code doesn't match a state.
        '''
        try:
            return US_State.objects.get(short=usps.upper())
        except US_State.DoesNotExist:
            return None

    def try_get_county(self, full_fips):
        '''
        Given a 5-digit FIPS code, split the code into state and county parts,
        try to query the state from the database, then try to query the county
        from the state. Returns none if either the county ot state are not matched
        by their respective portion of the FIPS code.
        '''
        state_fips = full_fips[0:2]
        county_fips = full_fips[2:6]
        try:
            state = US_State.objects.get(fips=state_fips)
            county = state.counties.get(fips=county_fips)
            return county
        except (US_State.DoesNotExist, US_County.DoesNotExist):
            return None

    def fips_list_decorator(self, context, data_set):
        '''
        Stage 4 of context processing:

        Use the GET array on the request to determine what counties are being requested.
        Two options: either
            ?state=TN -> use all the counties in that state
            ?county=23001,23002,34003,... -> use the counties listed by FIPs code

        Inputs: context, data set
        Outputs: context, data set, list of US_County
        Errors: No state matches the 'state' query string
        Warnings: A FIPS code was given that does not match a county
        '''
        # if the state parameter exists then we will use that and IGNORE any county parameter
        requested_state = self.request.GET.get('state', None)
        if requested_state is not None:
            # the state parameter might not match an actual state!
            state = self.try_get_state(requested_state)
            if state is None:
                msg = f"The USPS code '{requested_state}' doesn't match a US State"
                context['error'] = msg
                messages.error(self.request, msg)
                return (context, False, data_set) # stops the pipeline
            else:
                counties = [county for county in state.counties.all().iterator()]
                return (context, True, data_set, counties)
        else:
            # otherwise, look for a "county" parameter that lists 5-digit FIPs codes
            fips_str = self.request.GET.get('county', None)

            if fips_str is None:
                messages.warning(self.request, 'No counties were selected; this chart will only show the percentile distribution.')
                return (context, True, data_set, [])

            fips_list = fips_str.split(',')
            # list of pairs, (FIPs, County or None)
            query_results = [(fips, self.try_get_county(fips)) for fips in fips_list]
            # list of County
            counties = [county for (_, county) in query_results if county is not None]
            # list of FIPs that did not match a county
            missing = [fips for (fips, county) in query_results if county is None]

            if len(missing) > 0:
                missing_str = ", ".join(missing)
                context['unknown_fips'] = missing_str
                msg = f"The following FIPS codes did not match a county: {missing_str}"
                messages.warning(self.request, msg)

            return (context, True, data_set, counties)

    def data_point_decorator(self, context, data_set, counties):
        '''
        Stage 5 of context processing:
        Given a data set and list of counties, get data points for each of those counties
        and serialize them into HighCharts-friendly format.

        Inputs: context, data set, list of counties
        Outputs: context
        Errors: none
        Warnings: requested counties that did not have a data point in the data set
        '''

        # check if there is a data point for each requested county
        # this returns None if the query doesn't match
        # IMPORTANT to use both filters here, or you may get a data point for a county
        # with the same partial fips as the one you wanted, but from the wrong state!
        def try_get_point(county):
            state_fips = county.state.fips
            county_fips = county.fips
            return data_set.data_points.filter(county__state__fips=state_fips).filter(county__fips=county_fips).first()

        # list of pairs (County, Data_Point or None)
        maybe_points = [(county, try_get_point(county)) for county in counties]
        # list of valid data points
        have_value = [point for (_, point) in maybe_points if point is not None]
        # list of counties that did not have a data point in this data set
        missing_value = [county for (county, point) in maybe_points if point is None]

        # now convert all the valid points to dictionaries that we can serialize for HighCharts
        def point_to_struct(point):
            return {
                'x': point.rank * 100,
                'y': point.value,
                'name': point.county.name,
            }

        structs = [point_to_struct(p) for p in have_value]
        context['data_series'] = json.dumps(structs)

        # attach info about any counties that were not in the data set
        if len(missing_value) > 0:
            combined_str = ", ".join([str(c) for c in missing_value])
            context['missing_point'] = combined_str
            msg = f"The following counties did not have a value in this data set: {combined_str}"
            messages.warning(self.request, msg)

        return (context, True)

    # A helper function for chaining together context processing functions.
    # Each function must accept the current context as an argument, and must return a
    # tuple of *at least* (context, boolean) where the boolean indicates whether or not
    # to continue executing the next stage.
    # Stages can return additional values in the tuple, which will be passed as additional
    # arguments to the next function.
    # The number of additional arguments *returned* by stage N must match the number of
    # additional arguments *accepted* by stage N+1 !
    def decorate_context(self, context):

        decorators = [
            self.indicator_decorator,
            self.data_set_decorator,
            self.percentiles_decorator,
            self.fips_list_decorator,
            self.data_point_decorator,
        ]

        context, keep_going, other_args = context, True, []
        for dec in decorators:
            if not keep_going:
                break
            (context, keep_going, *other_args) = dec(context, *other_args)

        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.decorate_context(context)
        return context


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


class HomeView(TemplateView):
    template_name = 'hda_public/dashboard.html'


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
        states = US_State.objects.all().order_by('full')
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
            counties = associated_state.counties.order_by('name')

        return counties

# have identified a potential problem:
# assume 2 data sets for 1 indicator, one 2017 and one 2018
# let's say the 2017 data set includes county X, but set 2018 does NOT include county X
# when we collect indicators that contain county X, we will find the 2017 data set through
# the 2017 data point for county X, and hence find our indicator object.

# when we go to the chart view, we pass it 3 pieces of information: state, county, and indicator
# the chart view then looks up the latest data set for the given indicator (which will be the 2018 one)
# the data set that is plotted will not include county X, but the URL specifies that we should
# highlight county X.

# hmmm.

class HealthView(TemplateView):
    template_name = 'hda_public/health_indicator.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        fips = self.kwargs.get('fips', None)
        state_short = self.kwargs.get('short', None)

        if fips is not None and state_short is not None:
            # get the state the user wants
            state = US_State.objects.get(short=state_short.upper())
            # get the county the user wants
            county = state.counties.get(fips=fips)
            # make a list of every data set containing a data point connected to this county,
            # by starting with the county's data points and going backwards.
            # the 'select_related' does *not* affect the result of the query, only how many database queries are required.
            available_data_sets = [dp.data_set for dp in county.data_points.all().select_related('data_set')]
            # several data sets may be for the same indicator (perhaps different datasets for different years).
            # this extracts the indicator from each dataset into a list, then puts that list into a python set object,
            # which can remove the duplicates for us.
            unique_indicators = set([ds.indicator for ds in available_data_sets])
            # pack up the context - including whole objects so we can use multiple properties in the template
            context['state'] = state
            context['county'] = county
            context['indicators'] = unique_indicators
        else:
            context['error'] = 'Missing a valid state or county identifier in the URL for this page'

        return context
