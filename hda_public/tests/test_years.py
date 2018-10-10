from django.test import TestCase
from hda_privileged.models import Data_Point, Data_Set, Health_Indicator

class SampleGetYearsTest(TestCase):
    def setUp(self): 
        hi_name = "Obisity"
        ds = Data_Set.objects.all().filter(indicator__name = hi_name)
        years = [i.year for i in ds]
        self.assertEquals(years.count() == 4)

        # self.assertTrue(ds.exists())