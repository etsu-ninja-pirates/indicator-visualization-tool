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
        mystate = US_State()
        mycounty = US_County()
        for row in csv.DictReader(open('./data.csv')):           
            mystate.full   = row['full']
            mystate.short = row['short']
            mystate.fips       = row['fips']
            mystate.save()
            
        for row in csv.DictReader(open('./counties.csv', 'r')):           
            mystate = US_State.objects.filter(pk=row['state_id']).values
            for m in mystate: 
                # print(m.get('short'))
                
                # mycounty.state_id = m.get
                # print(m) 
                if m.get('short') == US_County.objects.filter(state_id=row['state_id']):
                #     # mstate.mycounty_set.create(name=row['name'], fips=row['fips'])
                #     mycounty.state_id = US_State.objects.filter(pk=row['state_id']).values()
                #     mycounty.fips = row['fips']
                #     mycounty.name = row['name']
                    print(m.get('short'))
                # mycounty.save()
                # print(US_County.objects.filter(state_id=row['state_id']).values()) 
                    


            
        