import json

from django.contrib import messages
from django.views.generic import TemplateView

from hda_privileged.models import Health_Indicator, US_State, US_County


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
    # Possible fix: make year a part of the path! So this view will now not only what indicator to use,
    # but what data set to use for that indicator, if there are several for different years!
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
            context['year'] = dataset.year
            context['data_set_id'] = dataset.id
            return (context, True)

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
        Tries to get the county object corresponding to a 5-digit FIPS code.
        '''
        try:
            return US_County.objects.get(fips5=full_fips)
        except US_County.DoesNotExist:
            return None

    # 3.a: what counties were requested? (Using the 'state' parameter)
    def state_request_decorator(self, context):
        requested_state = self.request.GET.get('state', None)

        # Guard: if there is no state query string,
        # do nothing and let the next context processing step proceed
        if requested_state is None:
            return (context, True)

        state = self.try_get_state(requested_state)
        if state is None:
            # the state parameter might not match an actual state!
            msg = f"The USPS code '{requested_state}' doesn't match a US State"
            context['error'] = msg
            messages.error(self.request, msg)
            return (context, False)  # stops the pipeline
        else:
            context['place_name'] = state.full
            context['counties'] = [county.fips5 for county in state.counties.all().iterator()]
            return (context, True)

    # 3.b: what counties were requested? (Using the 'county' parameter)
    def county_request_decorator(self, context):

        # Guard: if another decorator already added counties, do nothing!
        # (We could change this to merge additional counties if we wanted?)
        if 'counties' in context and len(context['counties']) > 0:
            return (context, True)

        # No counties added yet: try to get the 'county' parameter from GET query string
        fips_str = self.request.GET.get('county', None)

        # Guard: there was no paramater specifying what counties to show!
        if fips_str is None:
            messages.warning(self.request, 'No counties were selected; this chart will only show the percentile distribution.')
            return (context, True)

        fips_list = fips_str.split(',')
        # list of pairs, (FIPs, County or None)
        query_results = [(fips, self.try_get_county(fips)) for fips in fips_list]
        # list of County
        counties = [county for (_, county) in query_results if county is not None]
        # list of FIPs that did not match a county
        missing = [fips for (fips, county) in query_results if county is None]

        # include context for invalid/unknown FIPS codes
        if len(missing) > 0:
            missing_str = ", ".join(missing)
            context['unknown_fips'] = missing_str
            msg = f"The following FIPS codes did not match a county: {missing_str}"
            messages.warning(self.request, msg)

        # if we are only showing a single county,
        # add some extra context to make the view prettier
        if len(counties) == 1:
            c = counties[0]
            context['place_name'] = f"{c.name}, {c.state.short}"
            context['parent_state'] = c.state.short

        context['counties'] = [c.fips5 for c in counties]
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
            self.state_request_decorator,
            self.county_request_decorator,
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
