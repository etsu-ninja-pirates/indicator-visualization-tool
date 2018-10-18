from hda_privileged.models import *

def dataByYear(userYear, userIndicator=''):
    ds = Data_Set.objects.filter(year=userYear, indicator__name=userIndicator)
    return ds




