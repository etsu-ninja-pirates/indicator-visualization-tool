from csv import DictReader
import csv
from datetime import datetime
from django.core.management import BaseCommand
from hda_privileged.models import US_States, US_Counties
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
        if US_States.objects.exists(): 
            print('US States data is already in the Database. ')
            print(ALREADY_LOADED_ERROR_MESSAGE)

        elif US_Counties.objects.exists(): 
            print('US County data is already in the Database. ')
            print(ALREADY_LOADED_ERROR_MESSAGE)
            return

        print("Loading US State Data ")

        for row in csv.DictReader(open('./data.csv')):           
            mystate = US_States()
            mystate.state_name   = row['state_name']
            mystate.abbreviation = row['abbreviation']
            mystate.s_fips       = row['s_fips']
            mystate.save()
            
        for row in csv.DictReader(open('./counties.csv')):           
            mycounty = US_Counties()
            mycounty.s_fips   = row['s_fips']
            mycounty.abbreviation = row['abbreviation']
            mycounty.county_name  = row['county_name']
            mycounty.c_fips  = row['c_fips']
            mycounty.save()