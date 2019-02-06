import argparse
import json

from pathlib import Path

from django.core.management import BaseCommand, CommandError

from app_api.util import search
from hda_privileged.models import US_County

def pathtype(value):
    path = Path(value)
    if not path.parent.exists():
        raise argparse.ArgumentTypeError(f"Folder")

def indent_level(is_pretty):
    return 2 if is_pretty else None

def separators(is_pretty):
    return (',', ': ') if is_pretty else (',', ':')

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-o', '--output-path',
            type=pathtype,
            default=Path.cwd() / 'county_prefetch.json',
            help='File path to save prefetch data to'
        )
        parser.add_argument(
            '-p', '--pretty',
            action='store_true',
            help='Formats JSON for readability instead of compactness'
        )

    def handle(self, *args, **options):
        output_path = options['output_path']
        is_pretty = options.get('pretty', False)

        counties_query = US_County.objects.all().order_by('state', 'name')
        counties_data = [search.datum_for_county(c) for c in counties_query.iterator()]
        with output_path.open(mode='w') as fp:
            json.dump(
                counties_data,
                fp,
                indent=indent_level(is_pretty),
                separators=separators(is_pretty),
                sort_keys=is_pretty
            )
