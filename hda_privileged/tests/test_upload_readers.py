import csv
import tempfile
import unittest

from django.test import TestCase
from functools import reduce
from hda_privileged.models import (
    US_State,
    US_County,
    Health_Indicator,
    Data_Set,
    Data_Point
)
from hda_privileged.upload_reading import (
    CHOICE_NAME,
    CHOICE_1FIPS,
    CHOICE_2FIPS,
    get_county_reader,
    read_data_points_from_file
)

class GetCountyReaderTestCase(TestCase):

    # if you specify a value for choice that does not exist, return None
    def test_invalid_choice(self):
        self.assertIsNone(get_county_reader(""))

    # if you specify CHOICE_NAME, this should return a function Dict -> County
    # that queries the database using state and county names from the dict
    def test_name_choice(self):
        cases = [
            {'fips': '53069', 'State': 'Washington', 'County': 'Wahkiakum'},
            {'fips': '53069', 'State': 'Washington', 'County': 'Wahkiakum County'},
            {'fips': '72111', 'State': 'Puerto Rico', 'County': 'Peñuelas'},
            {'fips': '72111', 'State': 'Puerto Rico', 'County': 'Peñuelas Municipio'},
            {'fips': '13061', 'State': 'Georgia', 'County': 'Clay'},
            {'fips': '13063', 'State': 'Georgia', 'County': 'Clayton'},
        ]
        reader = get_county_reader(CHOICE_NAME)
        for case in cases:
            id = case['State'] + " + " + case['County']
            with self.subTest(county=id):
                county = reader(case)
                fips = county.state.fips + county.fips
                self.assertEqual(fips, case['fips'])

    # if you specify CHOICE_1FIPS, the function should use the 'FIPS' column
    def test_fips_choice(self):
        cases = [
            {'FIPS': '06037', 'State': 'California', 'sfips':'06', 'cfips':'037', 'County': 'Los Angeles County'},
            {'FIPS': '72033', 'State': 'Puerto Rico', 'sfips':'72', 'cfips':'033', 'County': 'Cataño Municipio'},
            {'FIPS': '01001', 'State': 'Alabama', 'sfips':'01', 'cfips':'001', 'County': 'Autauga County'},
        ]
        reader = get_county_reader(CHOICE_1FIPS)

        for case in cases:
            id = "{} + {}".format(case['State'], case['County'])
            with self.subTest(id=id):
                county = reader(case)
                self.assertEqual(county.state.fips, case['sfips'])
                self.assertEqual(county.fips, case['cfips'])
                self.assertEqual(county.name, case['County'])

    # if you specify CHOICE_2FIPS, the function should use the 'State' and 'County'
    # columns, but interpret them as partial FIPS codes
    def test_two_fips_choice(self):
        cases = [
            {'FIPS': '06037', 'State': '06', 'County': '037', 'sname': 'California', 'cname': 'Los Angeles County'},
            {'FIPS': '72033', 'State': '72', 'County': '033', 'sname': 'Puerto Rico', 'cname': 'Cataño Municipio'},
            {'FIPS': '01001', 'State': '01', 'County': '001', 'sname': 'Alabama', 'cname': 'Autauga County'},
        ]
        reader = get_county_reader(CHOICE_2FIPS)
        for case in cases:
            id = "{} + {}".format(case['sname'], case['cname'])
            with self.subTest(id=id):
                county = reader(case)
                fips = county.state.fips + county.fips
                self.assertEqual(fips, case['FIPS'])
                self.assertEqual(county.name, case['cname'])

    # this should explode - I'm including it because this spelling is how CHR
    # specifies this county, and I'm not sure how to handle that yet.
    @unittest.expectedFailure
    def test_LaSalle(self):
        reader = get_county_reader(CHOICE_NAME)
        row = {'State': 'Louisiana', 'County': 'La Salle'}
        county = reader(row)
        fips = county.state.fips + county.fips
        self.assertEqual(fips, '22059')

    def test_bad_county_name(self):
        reader = get_county_reader(CHOICE_NAME)
        row = {'State': 'Virginia', 'County': 'Not a county'}
        with self.assertRaises(US_County.DoesNotExist):
            reader(row)


    def test_bad_state_name(self):
        reader = get_county_reader(CHOICE_NAME)
        row = {'State': 'Not a state', 'County': 'Washington'}
        with self.assertRaises(US_State.DoesNotExist):
            reader(row)


# these are happy path tests
# TODO: test failures!
class ReadDataPointsFromFileTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        hi = Health_Indicator.objects.create(name='Test Indicator')
        ds = Data_Set.objects.create(indicator=hi, year=2900)
        # will be available in methods as self.test_data_set
        cls.test_data_set = ds

    def setUp(self):
        # so in-memory changes to the data set do not persist between test methods
        self.test_data_set.refresh_from_db()

    def test_name_scheme(self):
        rows = [
            ('State','County','Value'),
            ('Virginia','Washington','50.1'),
            ('Tennessee','Washington','60.2'),
            ('Puerto Rico','Mayagüez Municipio','70.3'),
        ]
        self.run_test_scheme(rows, CHOICE_NAME)

    def test_single_fips_scheme(self):
        rows = [
            ('FIPS','Value'),
            ('47179','1.0'),
            ('72097','2.0'),
        ]
        self.run_test_scheme(rows, CHOICE_1FIPS)

    def test_two_fips_scheme(self):
        rows = [
            ('State','County','Value'),
            ('47','179','2.0'),
            ('72','097','2.0'),
        ]
        self.run_test_scheme(rows, CHOICE_2FIPS)

    def run_test_scheme(self, rows, scheme):
        with tempfile.TemporaryFile(mode='w+', encoding='utf-8', newline='') as fp:
            writer = csv.writer(fp)
            writer.writerows(rows)
            fp.seek(0)

            data_points = read_data_points_from_file(fp, scheme, self.test_data_set)

            # check that the points have NOT been saved
            self.assertFalse(Data_Point.objects.all().exists())
            # check that we have as many data points as we had rows
            self.assertEqual(len(data_points), len(rows) - 1)
            # check that at least the first data point has the data set we specified
            self.assertEqual(data_points[0].data_set, self.test_data_set)
            # check that the type of the value is float
            self.assertIsInstance(data_points[0].value, float)
