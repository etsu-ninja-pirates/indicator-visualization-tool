from django.core.management import BaseCommand, CommandError
from hda_privileged.models import *

import argparse
import random
import math

from itertools import dropwhile, islice

def _create_data_set(indicator, year):
    # don't overwrite an exisitng data set!
    if indicator.data_sets.filter(year=year).exists():
        raise CommandError(f'Indicator {indicator.name} already has a data set for year {year}, aborting')
    else:
        # https://docs.djangoproject.com/en/2.1/topics/db/queries/#additional-methods-to-handle-related-objects
        return indicator.data_sets.create(year=year)

def _create_data_points(data_set, max_points):
    count = max_points if max_points else US_County.objects.count()
    make_point = lambda c: Data_Point(value=random.random(), county=c, data_set=data_set)
    counties = US_County.objects.all()[:count]
    return [make_point(c) for c in counties.iterator()]

# https://www.youtube.com/watch?v=_bK6iw-Fu0U
def _percentile_value(p, values):
    """
    Calculate the percentile (exclusive) for the given percentile (p)
    and list of values (values). Assumes values is sorted in ascending order,
    and p is in the range (0,1) (excludes the minimum and maximum)
    """
    n = len(values)
    # First, find the index in our range where a percentile value should be.
    # This will be a floating point number and may fall between two integer indicies,
    # in which case we'll have to interpolate!
    fp_index = (n+1) * p
    i_lower = min(math.floor(fp_index), n - 1)
    i_upper = min(math.ceil(fp_index), n - 1)

    if i_lower == i_upper:
        # we have an exact index, don't need to interpolate
        return values[i_lower]
    else:
        # must interpolate between two of our actual values
        # the two values in our list:
        v_lower = values[i_lower]
        v_upper = values[i_upper]
        # the space between those two values:
        diff = v_upper - v_lower
        # The fractional part of the index we found:
        frac = fp_index - v_lower
        # interpolate:
        pv = v_lower + (frac * diff)
        return (p, pv)

# assigns a percentile between 0 and 1 to each point e.g. if a point has the
# percentile .856, then the point # is in the 85.6th percentile -> 85.6% of
# the values are smaller than the point
# TODO: is it better to assign the percentile value instead, and calculate the indices as needed?
def _add_percentiles(points):

    # sort the list of points in place by value
    points.sort(key=lambda pt: pt.value)

    # produces 0.1...99.9 shifted two decimal places so values are all between 0 and 1
    percentiles = [n / 1000 for n in range(1,1000)]

    # Get a value for each percentile we want to calculate.
    # These values may fall between two actual values in our list of points
    # the list will be of tuples, `(percentile, percentile value)`
    values = [pt.value for pt in points]
    percentile_values = [_percentile_value(p, values) for p in percentiles]

    # assign a percentile to each point
    for pt in points:
        # skip percentiles until we find one with a value larger than the point's value
        percentile_values = list(dropwhile(lambda pv: pv[1] < pt.value, percentile_values))
        # assign that percentile (between 0 and 1) to the point
        (p, _) = percentile_values[0]
        pt.percentile = p
        # if we need the percentile value

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--indicator', default='Test Indicator')
        parser.add_argument('-y', '--year', type=int, default=2018)
        parser.add_argument('-m', '--max', type=int, default=None)

    def handle(self, *args, **options):
        indicator_name = options['indicator']
        year = options['year']
        max_points = options["max"]

        self.stdout.write(f"Creating random data for {indicator_name}, {year}")

        # https://docs.djangoproject.com/en/2.1/ref/models/querysets/#get-or-create
        indicator, _ = Health_Indicator.objects.get_or_create(name=indicator_name)
        data_set = _create_data_set(indicator, year)

        self.stdout.write(f"Using indicator w/ id {indicator.id}, data set w/ id {data_set.id}")

        random.seed()

        points = _create_data_points(data_set, max_points)
        self.stdout.write(f"Created {len(points)} new data points")

        self.stdout.write("Adding percentiles...")
        _add_percentiles(points)

        # this may not work properly?
        self.stdout.write("Saving data points")
        Data_Point.objects.bulk_create(points)

