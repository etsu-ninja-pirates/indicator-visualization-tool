from django.test import TestCase
from django.core.management import call_command

from hda_privileged.percentile import *

from math import isclose

class RankCalculationTestCase(TestCase):

    # with N = 0, the first case of p in [0, 1/(n+1)] becomes
    # p in [0, 1] which is always true - so this should always
    # return 1 no matter what percentile is requested.
    def test_zero_sample_size(self):
        for p in range(1,10):
            x = rank(p / 10, 0)
            self.assertEqual(x, 1)

    # with N = 1, the ranges become p in [0, 0.5] and p in [0.5, 1],
    # the second case whould never match, because its range is (0.5, 0.5).
    # (no values match this because the endpoints are both excluded and equal to each other.)
    # for values below 0.5, we should return 1, and for values above 0.5 we should return
    # sample_size - in this case the two are both 1, so the returned value should
    # always be 1 (again)
    def test_one_sample_size(self):
        for p in range(1,100):
            with self.subTest(p=p):
                x = rank(p / 100, 1)
                self.assertEqual(x, 1)

    # our calculation method does not allow percentiles of 0% or 100%
    # *this makes sense* because no value in a list of values is greater than 100%
    # of the values in the list - this would imply that the maximum value
    # is greater than itself. Throw an exception if given p = 0 or p = 1
    def test_excluded_percentile(self):
        with self.assertRaises(PercentileBoundsError) as context:
            rank(0, 100)

        with self.assertRaises(PercentileBoundsError) as context:
            rank(1, 100)

    # the first case has an inclusive boundary at 1/N+1
    # for a sample size of 2, this is at 33%
    def test_lower_boundary(self):
        n = 2
        p1 = 0.33  # 33%
        p2 = 0.34 # 34%

        self.assertEqual(rank(p1, n), 1)
        # can't use assertEqual here b/c floating point numbers
        self.assertAlmostEqual(rank(p2, n), p2 * (n + 1))



