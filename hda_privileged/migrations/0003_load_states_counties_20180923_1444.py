# Generated by Django 2.0.3 on 2018-09-23 18:44

from django.db import migrations
from csv import DictReader

STATE_FILENAME = "./data/states.csv"
COUNTY_FILENAME = "./data/counties.csv"


def load_data(filename, fn):
    """
    Given a filename and a function - open the file with CSV DictReader,
    and pass each row read from the file into the function. Return a list
    of the results, i.e. map(f, rows)
    """
    with open(filename) as csvf:
        return [fn(r) for r in DictReader(csvf)]


def make_state(state_model):
    """
    Given a US_State model class to use, returns a function that
    takes a DictReader row and returns a US_State instance
    """
    return lambda row: state_model(
        full=row['NAME'],
        short=row['USPS'],
        fips=row['FIPS']
    )


def make_county(county_model, state_map):
    """
    Given a US_County model class to use and a dictionary mapping State USPS
    codes to US_State objects, returns a function that takes a DictReader row
    and returns a US_County object
    """
    return lambda row: county_model(
        fips=row['FIPS'],
        name=row['NAME'],
        state=state_map[row['STATE_USPS']]
    )


def load_states_and_counties(apps, schema_editor):
    # get the correct version of the state model for the point in history
    # where this migration lives (importing will always get the newest version
    # of the model class, and you don't want that in a migration)
    US_State = apps.get_model('hda_privileged', 'US_State')
    # load state objects from CSV file
    states = load_data(STATE_FILENAME, make_state(US_State))
    # save the state instances to the DB
    for s in states:
        s.save()

    # as above: get the correct version of the county model for this migration
    US_County = apps.get_model('hda_privileged', 'US_County')
    # produces a map of state shortnames/USPS codes to state objects - this lets us
    # look up state objects without hitting the database
    state_map = {s.short: s for s in states}
    # load county objects from CSV file
    counties = load_data(COUNTY_FILENAME, make_county(US_County, state_map))
    # create all the county objects in a single query, otherwise this will take forever
    US_County.objects.bulk_create(counties)


class Migration(migrations.Migration):

    dependencies = [
        ('hda_privileged', '0002_auto_20180921_1706'),
    ]

    operations = [
        migrations.RunPython(load_states_and_counties),
    ]
