from csv import DictReader
import csv
from datetime import datetime
from django.core.management import BaseCommand
from hda_privileged.models import US_County, Health_Indicator, Data_Set, Data_Point, US_State

# from pytz import UTC

DATETIME_FORMAT = '%m/%d/%Y %H:%M'

# This Message should only be displayed for the development site not production.
# In production the data should only be input once, fo the States and counties.
# The data for County and State will be updates on a need basis.

ALREADY_LOADED_ERROR_MESSAGE = """
If you need to reload the County - State data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables
"""


class Command(BaseCommand):
    # Return the message below when Help is types
    help = "Loads the data from \"your_filename.csv\" into the models "

    # inputting the name of the indicator and the respective year
    indicator_a = Health_Indicator(name='Obesity')
    indicator_a.save()

    #associated_indicator = Health_Indicator.objects.get(name='Obesity')

    data_set_a = Data_Set(indicator= indicator_a, year='2018-09-19', source='Dummy Data')

    data_set_a.save()

    # open the file from the specified path
    f = open('./data/dummydata.csv', 'r')

    # reading the value from the selected file
    for row in csv.DictReader(f):
        # name=row['name'],
        s_fips = row['s_fips']
        full = row['full']
        county = row['fips'].strip()
        percentile = row['percentile']
        state = row['state_id']

        associated_state = US_State.objects.get(short=state)
        associated_county = associated_state.counties.filter(fips=county).first()
        if associated_county is None:
            raise Exception(f"OH NO : couldn't find an object instance for {county}")

        # associated_county = US_County.objects.get(name=county, state=associated_state.short)
        data_point_a = Data_Point(
            county=associated_county,
            percentile=percentile,
            data_set=data_set_a
        )
        data_point_a.save()

    # print("Loading Data_Set")
