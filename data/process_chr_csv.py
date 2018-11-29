# usage: process_chr_csv.py PATH_TO_CSV [ID:NAME]+
# where ID is an ID from:
# http://www.countyhealthrankings.org/sites/default/files/CHR2018_CSV_SAS_documentation.pdf
# corresponding to a measure appearing in:
# http://www.countyhealthrankings.org/sites/default/files/chr_measures_CSV_2018.csv
import argparse
import csv
import pathlib

INPUT_STATE_HEADER = 'FIPS State Code'
INPUT_COUNTY_HEADER = 'FIPS County Code'


# expects path to an accessible CSV file, return Path
def csv_path(value):
    path = pathlib.Path(value)
    if not path.is_file():
        raise argparse.ArgumentTypeError('File is missing or inaccessible')
    elif path.suffix.lower() != '.csv':
        raise argparse.ArgumentTypeError('File is not a CSV file')
    return path


def folder_path(value):
    path = pathlib.Path(value)
    if not path.is_dir():
        raise argparse.ArgumentTypeError('Path is not a directory!')
    return path


# expects 'INT:STRING', returns (int, str)
def column_spec(value):
    (column, sep, name) = value.partition(':')
    return (int(column), name)


class MeasureOutput():
    def __init__(self, id, name, output_dir_path):
        # generate the name of the value column we will look for
        self.value_header = f'measure_{id:d}_value'
        # create a file in the output directory
        file_name = f'({id:d}) {name}.csv'
        file_path = output_dir_path / file_name
        self.file = file_path.open('w', newline='')
        self.writer = csv.DictWriter(self.file,
                                     fieldnames=('State', 'County', 'Value'),
                                     quoting=csv.QUOTE_NONNUMERIC)
        self.writer.writeheader()

    def process(self, row):
        state_fips = row[INPUT_STATE_HEADER]
        county_fips = row[INPUT_COUNTY_HEADER]
        value = row[self.value_header]
        if value:
            to_write = {
                'State': state_fips,
                'County': county_fips,
                'Value': float(value)
            }
            self.writer.writerow(to_write)

    def finish(self):
        self.file.close()


def main():
    parser = argparse.ArgumentParser(
        description='''Takes a CSV file downloaded from County Health Rankings and
        extracts specific columns, outputting a new CSV file for each extracted column.
        This can be used to generate a lot of uploadable files for the CHR Indicator
        Visualization Tool in one operation. Because the CHR CSV/SAS data is specified
        using numeric IDs, this requires you to specify the ID of the column to extract
        along with a name to associate with that column. The script will then extract values
        from the input file column with name 'measure_ID_value' and write them to a file
        that includes the corresponding name.
        '''
    )
    parser.add_argument('CHR_CSV_FILE',
                        type=csv_path,
                        help='Path to accessible CSV file downloaded from CHR')
    parser.add_argument('COLUMN',
                        nargs='+',
                        type=column_spec,
                        help='''ID:NAME where ID is an integer corresponding to a
                            CHR measure ID, and a name to describe the measure.
                            Can enclose multi-word names with double-quotes.''')
    parser.add_argument('-o', '--output',
                        metavar='OUTPUT_FOLDER',
                        type=folder_path,
                        default='.',
                        help='Path to existing directory to write output files to')
    args = parser.parse_args()

    # create objects for all our output files
    outputs = [MeasureOutput(mid, name, args.output) for (mid, name) in args.COLUMN]

    # output to each file for each row in the input
    with args.CHR_CSV_FILE.open('r', newline='') as csv_in:
        reader = csv.DictReader(csv_in)
        for row in reader:
            for output in outputs:
                output.process(row)

    # close all the files
    for output in outputs:
        output.finish()


if __name__ == '__main__':
    main()
