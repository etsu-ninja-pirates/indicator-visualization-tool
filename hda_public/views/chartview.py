# ChartView - Django View for a single large Highcharts plot containing a single data set
# and some number of counties. Capable of plotting arbitrary counties using a comma-separated
# list of 5-digit FIPS codes included in the URL query string (an HTTP GET parameter).
# ~ Matthew Seiler

from django.contrib import messages
from django.views.generic import TemplateView

from hda_privileged.models import Health_Indicator, US_State, US_County


class ChartView(TemplateView):
    """
    Works with URLs of the following shape:
    - a keyword path parameter called 'indicator', which is an integer Health_Indicator ID
    - one of two query strings to specify what counties to display:
       + `?state=<USPS>`, where <USPS> is a 2-letter USPS postal code for a state
       + `?county=<FIPS_LIST>`, where <FIPS_LIST> is comma-separated list of *5-digit* FIPs codes

    Examples:
    * /chart/3?state=TN
    * /chart/3?county=01002,01005,01007

    The view will retrieve the *most recent data set* for the requested Health Indicator, if one
    exists. It will validate the requested counties - creating a list of FIPS codes for all the
    counties in the requested state, or filtering requested FIPS codes to ones which match a
    county in the database. It includes the data set ID and list of counties in the template
    context, but *does not* query or attach the contents of the data set! (We rely on client-side
    JavaScript to request the chart series for the data set.)

    Each stage of context processing is broken into a separate function. Each function takes in
    the context dictionary and additional state from the previous stage, augments the context
    object in some way, and returns the updated context, a flag indicating whether to halt
    processing, and any additional state the next stage will require. The stages are listed in
    order and executed in the `decorate_context` function.
    """

    template_name = 'hda_public/chart.html'

    def indicator_decorator(self, context):
        """
        Adds a health indicator object to the context based on the indicator ID given in the
        'indicator' view keyword argument (self.kwargs). If no indicator matching the given ID
        exists, then an error message is added to context under the 'error' key, and also added
        to the messages framework with the 'error' tag.

        Matches the signature required by the 'decorate_context' helper method - returns a tuple
        (context, flag, *) where the first member is the augmented context, the second is a
        boolean indicating if the next processing stage should execute, and other members are
        arguments for the next context processor.

        :param context: template context dictionary
        :type context: dict
        :raises TypeError: TypeError if there is no 'indicator' key in self.kwargs
        :return: augmented context, continue flag, and indicator
        :rtype: (dict, True, Health_Indicator) | (dict, False)
        """

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


    # FIXME: this always gets the most recent data set, which may not include the county the user requested
    # (they may have asked for a county that is only included in an older data set for the same indicator!)
    # Possible fix: make year a part of the path! So this view will now not only what indicator to use,
    # but what data set to use for that indicator, if there are several for different years!
    def data_set_decorator(self, context, indicator):
        """
        Given a Health_Indicator, retrieves the most recent data set for that indicator, and adds
        the data set ID and year of the data set to the context. If there are no data sets for the
        given indicator, adds a an error message to the context (under the 'error' key) and to the
        messages framework.

        Matches the signature required by the 'decorate_context' method, but requires the previous
        decorator to pass through a health indicator object.

        :param context: template context
        :type context: dict
        :param indicator: health indicator of interest
        :type indicator: Health_Indicator
        :return: augmented context and continue flag
        :rtype: (dict, bool)
        """
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
        """
        Attempt to query a specific US_State from the data model, returning None if it is missing

        :param usps: ID of the state to retrieve, a 2-letter USPS code
        :type usps: str
        :return: the US_State matching the given USPS code
        :rtype: US_State | None
        """
        try:
            return US_State.objects.get(short=usps.upper())
        except US_State.DoesNotExist:
            return None

    def try_get_county(self, full_fips):
        """
        Attempt to query a specific county from the data model, returning None if it is missing

        :param full_fips: a 5-digit FIPS code for a county or county-equivalent
        :type full_fips: str
        :return: the county matching the given FIPS code
        :rtype: US_County | None
        """
        try:
            return US_County.objects.get(fips5=full_fips)
        except US_County.DoesNotExist:
            return None

    def state_request_decorator(self, context):
        """
        Looks for an HTTP GET parameter named 'state', and uses it to add a list of county FIPS
        codes to the context. Does nothing to the context if the 'state' parameter is missing
        (including not halting processing - we want to let another function add counties instead).


        If the requested state exists, adds the full name of the state under the 'place_name' key,
        for use in the chart title; and a list of 5-digit FIPS codes to the 'counties' key
        including each county in the state. (This may include counties that are not in the data set!)

        If the requested state does not exist, adds an error message to the context and to the
        message framework, and returns a 'False' flag in the return tuple to stop future functions
        from executing.

        Matches the signature required by 'decorate_context'.

        :param context: template context dictionary
        :type context: dict
        :return: augmented context and flag
        :rtype: (dict, bool)
        """

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
            # current_state added to pass in url param when user chooses to go from
            # all counties chart to county selection page: Kim Hawkins
            context['current_state'] = state.short
            context['counties'] = [
                county.fips5 for county in state.counties.all().iterator()]
            return (context, True)

    def county_request_decorator(self, context):
        """
        Looks for an HTTP GET parameter named 'county', and uses this to add county FIPS codes
        to the context. Does nothing if the context already contains a non-empty list under the
        key 'counties'.

        The 'county' query string should be a comma-separated list of 5-digit FIPS codes. This
        function queries for each of these FIPS codes to determine if that county actual exists
        in the data model. FIPS codes which do not match a county object are concatenated into
        a string which is added to the context under the 'unknown_fips' key, and to the messages
        framework at the 'warning' level.

        If only a single county was requested, the context is further augmented with 'place_name'
        and 'parent_state' keys, which are used to make a prettier chart title and a button that
        links to a chart of all the counties in the same state.

        :param context: template context dictionary
        :type context: dict
        :return: tuple of augmented context and flag for decorate_context
        :rtype: (dict, bool)
        """


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

    def decorate_context(self, context):
        """
        A helper function that chains several other functions together, each of which takes in
        a context dictionary and returns the same dictionary after adding something to it.
        This forms a pipeline of functions that the context passes through before finally being
        returned, wherein a little more information is added to the context at each step.

        The helper functions for pipeline steps should have the following signature:

            (dict, *) -> (dict, bool, *)

        where the bool signifies whether the pipeline should be allowed to continue. (This allows
        a step to prevent the pipeline from continuing if it encountered an irrecoverable error.)
        Any additional values returned from a step (the *) are passed, unpacked, as arguments to
        the next processing step.

        :param context: template context dictionary
        :type context: dict
        :return: template context dictionary, augmented with more keys
        :rtype: dict
        """

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
        """
        Returns template context data that TemplateView sends through to the template

        :return: template context
        :rtype: dict
        """

        context = super().get_context_data(**kwargs)
        context = self.decorate_context(context)
        return context
