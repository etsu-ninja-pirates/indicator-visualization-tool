from hda_privileged.models import Data_Set
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

DEMO_INDICATOR = 'Obesity'

def dataSetForYear(year, indicator_name=DEMO_INDICATOR):
    try:
        # get throws exceptions if more than one result matches the query
        result = Data_Set.objects.get(year=year, indicator__name=indicator_name)
        return result
    except ObjectDoesNotExist:
        # if nothing matched the query, swallow that exception and return None
        return None
    except:
        # in any other case (including MultipleObjectsReturned), re-raise the exception
        raise

# This method will be used to test the return of all the data sets pointing to a particular year
def dataSetYearsForIndicator(indicator_name=DEMO_INDICATOR):
    """ This function takes in a KPI name then returns all the years liked to it """
    results = Data_Set.objects.all().filter(indicator__name = indicator_name).order_by('year')
    return [ds.year for ds in results]


