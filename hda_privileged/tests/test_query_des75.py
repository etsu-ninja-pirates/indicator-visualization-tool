from django.test import TestCase
from django.core.management import call_command
from hda_public.templates.hda_public.QuerybyYear import *
from hda_privileged.models import Health_Indicator, Data_Set

class UserVarSelect(TestCase):

    # setUp runs once before each of the other test cases,
    # so we can use it to set up things that all of our test
    # cases will need.
    def setUp(self):
        # for instance, we'll probably want at least one health indicator to
        # exist, so we can use it when setting up our other tests.
        # By saving it as a property of "self", our other tests will be
        # able to access it as a property/attribute
        self.indicator_name = 'A Test Indicator'
        self.health_indicator = Health_Indicator(name=self.indicator_name)
        self.health_indicator.save()

    # 1. Set up the inputs/environment for the test
    # (in our case, this means creating things for the database)
    # 2. Perform the operation that we want to test (dataByYear)
    # 3. Check whether the results are what we expect (assert)
    def test_dataset_returned(self):
        name = "Dataset returned"
        # 1. add a data set to our sandbox database
        Data_Set.objects.create(indicator=self.health_indicator, year=2018)
        # 2. now try to retrieve it using our method
        # (For the current implementation of dataByYear, we must include an indicator name)
        setReturned=dataByYear(2018, userIndicator=self.indicator_name)
        # 3. check that we get what we expect - the QuerySet should have at least one result
        self.assertTrue(setReturned.exists())

    # This is a good test idea: make sure the year of the result matches the one you ask for
    def test_correct_year_returned(self):
        name = "Correct year returned"
        correctYear = dataByYear(2018)
        # since the result is a QuerySet, we need to use .first() to extract the first object in the list of results
        self.assertEqual(correctYear.first().year, 2017)

    # Also a reasonable idea: but AssertEqual/NotEqual might not be what you want here.
    # Comparing the two QuerySets for equality might not do what we expect!
    # Since QuerySet is a class, what happens here depends on whether QuerySet defines an __eq__ method
    # (just like equals() in Java) and if so, what that implementation is.
    # So it may be easier to compare the attributes or contents of the QuerySets.
    def test_assertYearEqual(self):
        first = dataByYear(2018)
        second = dataByYear(2017)
        self.assertEqual(first, second)





