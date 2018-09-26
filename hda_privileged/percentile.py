from math import ceil, floor
from itertools import dropwhile

class PercentileBoundsError(ArithmeticError):
    """
    We cannot calculate all percentiles for all sets of values, e.g.
    p = 0 or 1 are always invalid, or we may have an empty value list.
    In these cases we throw this exception to indicate that there was
    a problem with the percentile calculation.
    """
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message

def rank(percentile, sample_size):
    """
    Returns the rank (x) for a percentile (p) in a given sample size (N).
    Uses the Third Variant described here:
    https://en.wikipedia.org/wiki/Percentile#Third_variant
    which is the primary variant recommended by the NIST and corresponds to
    the PERCENTILE.EXC function in Excel.

    The percentile (p) is a floating point value between 0 and 1, exclusive
    (i.e. it cannot include 0.0 or 1.0)

    The sample size (N) is the number of values under consideration.

    The returned value (rank, denoted as x in the Wiki article) is the location
    in an ordered list of values of size N where the percentile value for percentile p
    is found. It is 1-based (the first rank is 1, not 0!) and may be a floating point
    value - indicating that the percentile value should be interpolated between
    two values in the list.
    """
    lower_bound = 1 / (sample_size + 1)
    upper_bound = sample_size / (sample_size + 1)

    # bounds checking: cannot calculate rank for 0% or 100%
    if percentile in (0,1):
        raise PercentileBoundsError(f"Cannot calculate percentile rank for p = 0 or p = 1 (was {percentile:d})")

    # edge conditions: cannot calculate a 'real' rank for all
    # percentiles and all sample sizes - percentile.exc has a restricted range
    if percentile <= lower_bound:
        return 1
    elif percentile >= upper_bound:
        return sample_size
    else:
        return percentile * (sample_size + 1)

def percentile(p, values):
    """
    Calculates the percentile value for a given percentile in a list of values.
    Assumes that the values are pre-sorted in ascending order. Uses an exclusive
    range ranking function, so the percentile must not be 0 or 1. Uses linear
    interpolation to determine percentile values that fall between two values in the list.

    See https://en.wikipedia.org/wiki/Percentile#Worked_example_of_the_third_variant
    """

    sample_size = len(values)

    if sample_size == 0:
        raise PercentileBoundsError("Can't calculate percentile with no values!")

    x = rank(p, sample_size)

    # the rank uses 1-based indices - subtract 1 to get a 0-based index for Python lists
    index = floor(x) - 1
    # python cleverly allows us to use `mod 1` to isolate the fractional part of a number
    fraction = x % 1

    # if the index is for the last element in the list, then we can't do linear interpolation
    # because there is no element at index + 1. In this case, the fractional part of the index
    # *should* always be 0 - it would not make sense to have a rank of N + some fraction.
    if x >= sample_size:
        # `values[index + 1]` will fail, so don't interpolate
        return values[index]
    else:
        # interpolate between the two values
        lower = values[index]
        upper = values[index + 1]
        return lower + fraction * (upper - lower)

def get_percentile_values(plist, values):
    """
    Produce a list of (rank, value) given a list of percentiles to calculate
    and values to draw percentiles from.

    percentiles - a list of percentage ranks to get percentile values for, e.g.
    [0.1, 0.2, 0.99] would get the 10th, 20th, and 99th percentiles

    values - a list of values to use when calculating the percentiles.
    *Must be pre-sorted in ascending order*

    Returns a list of tuples (p, v) where p is the percentile (e.g. 10th, 25th, 99th etc.)
    and v is the value for that percentile in the provided list
    """
    return [(p, percentile(p, values)) for p in plist]

def add_percentiles_to_points(points, plist=None):
    """
    Takes a list of data points, sorts them base on their "value" attribute,
    calculates the percentiles for every p in plist, and sets the "percentile"
    attribute on each data point object to the percentile where it fits.

    If no list/sequence of percentiles to calculate (plist) is given, then uses
    the 0.1% through 99.9% percentiles in steps of 0.1% (this is much to granular
    to be meanigful for data sets of less than 1000 points!)

    The list of points is mutated in place.

    Changes to the data model are *not* saved.

    Technically sunce python uses Duck Typing, the points can be *any* object
    that has both a "value" attribute and a "percentile" attribute.
    """

    # sort the list of points in place by value
    points.sort(key=lambda pt: pt.value)

    # percentiles - use argument or default
    # default produces 0.1 through 99.9 shifted 2 decimal places so values are in (0,1)
    percentiles = plist if plist else [n / 1000 for n in range(1,1000)]

    # extract the values so we can use them to calculate percentile results
    values = [pt.value for pt in points]
    # create our list of tuples (p, pv)
    percentile_values = get_percentile_values(percentiles, values)

    # assign a percentile to each point
    for pt in points:
        # skip percentiles until we find one with a value larger than the point's value
        percentile_values = list(dropwhile(lambda pv: pv[1] < pt.value, percentile_values))
        # it's possible that some value are larger than the largest percentile value we were asked to calculate!
        # in that case they don't fit in any of the "buckets" we have, so we'll run out of values here
        if len(percentile_values) == 0:
            break
        else:
            # assign that percentile (between 0 and 1) to the point
            (p, _) = percentile_values[0]
            pt.percentile = p
