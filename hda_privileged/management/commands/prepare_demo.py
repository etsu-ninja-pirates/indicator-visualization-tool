from io import StringIO

from django.core.management import BaseCommand, CommandError, call_command
from django.contrib.auth import get_user_model

from hda_privileged.models import *

DEMO_INDICATOR = "Obesity"
STARTING_YEARS = (2013,2015,)

class Command(BaseCommand):

    def handle(self, *args, **options):

        # clear the database (?)
        # call_command('flush')

        # run migrations
        call_command('migrate')

        # create a superuser
        User = get_user_model()
        User.objects.create_superuser('admin', 'admin@example.com', 'demo')

        # create starting data sets
        for year in STARTING_YEARS:
            call_command(
                'load_random_data_set',
                f'--indicator={DEMO_INDICATOR}',
                f'--year={year}')
