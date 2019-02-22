from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.db.models import Count

from hda_privileged.models import US_State, US_County, Health_Indicator, Data_Set, Data_Point

def key_selector(key):
    return lambda x: x[key]

def group_by_selector(items, selector):
    '''Group a list of items by using a provided function to produce a grouping key from items in the list.
    items :: list T
    selector :: T -> K
    returns :: dict K (list T)
    i.e. each key in the dictionary maps to a list of items from the original list that matched that key.
    The key for each item is produced by passing that item to the selector function.
    '''
    result = dict()
    for item in items:
        key = selector(item)
        if key not in result:
            result[key] = []
        result[key].append(item)
    return result

def group_by(selector):
    '''"Curried" version of group_by_selector that lets us specify the selector now to create
    a grouping function that we can pass items to later.
    selector :: T -> K
    returns :: list T -> dict K (list T)
    '''
    return lambda items: group_by_selector(items, selector)

class IndicatorOverviewBase(View):

    def handle_missing_parameter(self):
        # TODO: redirect to place selection?
        pass

    def get_chart_location_parameter(self):
        """
        Get the query string paramater to use when building URLs that request a chart or chart
        data for the requested location (e.g. "state=VA" or "county=12345")
        :return: the query string parameter with chart URLs in the template
        :rtype: str
        """
        pass

    def get_place_name(self):
        """
        Return a string to use for the name of the requested location.
        Subclasses MUST implement this!
        :return: a display-able name for the requested county or state
        :rtype: str
        """
        pass

    def get_related_data_sets(self):
        """
        Return every data set containing a data point for the requested location.
        Subclasses MUST implement this!
        :return: query set of data sets related to the requested location
        :rtype: QuerySet<Data_Set>
        """
        pass

    def get(self, request, *args, **kwargs):
        # every data set related to the requested location
        data_set_meta = self.get_related_data_sets().values('id', 'year', 'indicator')
        # group these data sets by indicator
        grouped_by_indicator = group_by_selector(
            data_set_meta.iterator(),
            key_selector('indicator')
        )
        # sort each group by year, descending
        for (_, dsm) in grouped_by_indicator.items():
            dsm.sort(key=key_selector('year'), reverse=True)
        # now change the map so each indicator ID points to only the ID of the most recent data set:
        data_set_for_indicator = {ind: dsm[0]['id'] for (ind, dsm) in grouped_by_indicator.items()}

        # at this point, we know what data sets and indicators are available, but we don't
        # actually have the full indicator objects queried from the database.
        # We'll need at least the indicator names, and which ones are "important"

        # What has to go on this page?
        # 1. One chart for each important indicator
        #    a. indicator name
        #    b. data set ID
        #    c. county/counties to plot
        # 2. One link for each indicator
        #    a. indicator name (for display)
        #    b. data set ID (for URL)
        #    c. county or counties (for URL)

        # So it's the same for each. Let's get all our indicator objects:
        indicator_ids = set(data_set_for_indicator.keys())
        indicators = Health_Indicator.objects.filter(id__in=indicator_ids)

        # whew. now let's build a list of dictionaries to use in context
        def make_indicator_ctx(indicator):
            return {
                'name': indicator.name,
                'data_set_id': data_set_for_indicator[indicator.id]
            }

        all_indicator_context = []
        important_indicator_context = []
        for indicator in indicators:
            ctx = make_indicator_ctx(indicator)
            all_indicator_context.append(ctx)
            if indicator.important:
                important_indicator_context.append(ctx)

        context = dict()

        context['all_indicators'] = all_indicator_context
        context['important_indicators'] = important_indicator_context
        context['place_name'] = self.get_place_name()
        context['place_query_string'] = self.get_chart_location_parameter()

        return render(request, 'hda_public/overview.html', context=context)


class IndicatorOverviewCounty(IndicatorOverviewBase):

    def get_chart_location_parameter(self):
        return f"county={self.county.fips5}"

    def get_place_name(self):
        county_name = self.county.name
        state_name = self.state.short
        return f"{county_name}, {state_name}"

    def get_related_data_sets(self):
        # get all the data points this county is in:
        dps = self.county.data_points.all()
        # then get all the data sets that have one of those data points:
        return Data_Set.objects.filter(data_points__in=dps)

    def get(self, request, state=None, county=None):
        if state is None or county is None:
            return self.handle_missing_parameter()

        try:
            self.state = US_State.objects.get(pk=state.upper())
        except US_State.DoesNotExist:
            return self.handle_missing_parameter()

        try:
            self.county = self.state.counties.get(fips=county)
        except US_County.DoesNotExist:
            return self.handle_missing_parameter()

        return super(IndicatorOverviewCounty, self).get(request)


class IndicatorOverviewState(IndicatorOverviewBase):
    def get_chart_location_parameter(self):
        return f"state={self.state.short}"

    def get_place_name(self):
        return f"{self.state.full}"

    def get_related_data_sets(self):
        # get all the counties in the state:
        counties = self.state.counties.all()
        # get all the data points that point at one of the counties:
        dps = Data_Point.objects.filter(county__in=counties)
        # then get all the data sets that have one of those data points:
        return Data_Set.objects.filter(data_points__in=dps)

    def get(self, request, state=None):
        if state is None:
            return self.handle_missing_parameter()

        try:
            self.state = US_State.objects.get(pk=state.upper())
        except US_State.DoesNotExist:
            return self.handle_missing_parameter()

        return super(IndicatorOverviewState, self).get(request)

class CannotFindThatPlace(View):
    # TODO: templates and stuff
    def get(self, request, message="Can't find that place"):
        return django.http.response.HttpResponse(message)