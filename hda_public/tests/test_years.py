from django.test import TestCase
from hda_privileged.models import Data_Point, Data_Set, Health_Indicator
from hda_public.views import showallYears

class SampleGetYearsTest(TestCase):
    def setUp(self): 
        self.hi = Health_Indicator(name = 'Obisity')
        self.hi.save()
        
    
    def test_years_returned(self):
        Data_Set.objects.create(indicator=self.hi, year = 2016)
        years = showallYears('Obisity')
        self.assertEqual(years, [2016])


        # self.assertTrue(ds.exists())