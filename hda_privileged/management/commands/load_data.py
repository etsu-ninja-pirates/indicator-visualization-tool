from csv import DictReader
import csv
from datetime import datetime
from django.core.management import BaseCommand
from hda_privileged.models import US_State, US_County
from pytz import UTC 

DATETIME_FORMAT = '%m/%d/%Y %H:%M'


# This Message should only be displayed for the development site not production. 
# In production the data should only be input once, fo the States and counties. 
# The data for County and State will be updates on a need basis. 

ALREADY_LOADED_ERROR_MESSAGE="""
If you need to reload the County - State data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables
"""

class Command(BaseCommand):
    # Return the message below when Help is types 
    help = "Loads the data from \"your_filename.csv\" into the models "
    
    
    def handle(self, *args, **options):
        if US_State.objects.exists(): 
            print('US States data is already in the Database. ')
            print(ALREADY_LOADED_ERROR_MESSAGE)

        elif US_County.objects.exists(): 
            print('US County data is already in the Database. ')
            print(ALREADY_LOADED_ERROR_MESSAGE)
            return


        print("Loading US State Data ")

        for row in csv.DictReader(open('./data.csv')):
            # easier to make a brand new state object every iteration
            a_state = US_State(
                full=row['full'],
                short=row['short'],
                fips=row['fips']
            )
            a_state.save()

        print("Loading US County Data ")

        # TODO can we speed this up with some kind of bulk insert?
        for row in csv.DictReader(open('./counties.csv')):
            fips = row['fips']
            name = row['name']
            state = row['state_id']

            # use whatever the primary key field of US_State is to
            # get exactly one state object
            # TODO error handling: what if the state code in the county
            # CSV file is malformed?
            # TODO this is slow for states with lots of counties;
            # we could cache the state objects in a dictionary to speed it up?
            associated_state = US_State.objects.get(short=state)

            a_county = US_County(
                fips=fips,
                name=name,
                state=associated_state)
            a_county.save()