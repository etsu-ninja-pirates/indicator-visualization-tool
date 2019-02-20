# Carves individual CSV files compatible with our uploader from a County Health Rankings CSV file.
# County Health Rankins reports all measures in one large CSV document, and assigns numeric IDs to
# each measure (indicator) it contains. This script allows you to specify what IDs to extract along
# with a label for that measure, and writes the values for that measure to a new CSV file that will
# work with our uploader.
#
# USAGE: process_chr_csv.py PATH_TO_CSV [ID:NAME]+
# where ID is an ID from:
# http://www.countyhealthrankings.org/sites/default/files/CHR2018_CSV_SAS_documentation.pdf
# corresponding to a measure appearing in:
# http://www.countyhealthrankings.org/sites/default/files/chr_measures_CSV_2018.csv
#
# EXAMPLE(S)
# > python process_chr_csv.py ".\chr_measures_CSV_2018.csv" 1:Mortality 11:Obesity 5:"Bad mental health days"
# This will output 3 files to the current directory:
# "(1) Mortality.csv", "(11) Obesity.csv", and "(5) Bad mental health days.csv"
# ...containing values read from the columns:
# "measure_1_value", "measure_11_value", and "measure_5_value", respectively.
#
# An actual command I ran in powershell:
# > python .\process_chr_csv.py `
#     "D:\Documents\School\csci5930\data\CHR\chr_measures_CSV_2018.csv" `
#     1:"Premature Death" 36:"Poor Physical Health Days" 42:"Poor Mental Health Days" `
#     9:"Adult Smoking" 85:"Uninsured" 4:"Primary Care Physicians" 69:"Some College" `
#     23:"Unemployment" 24:"Children in Poverty"
#
# Matthew Seiler
import argparse
import csv
import pathlib

# Column in the CHR file that contains the State FIPS code for the current row
INPUT_STATE_HEADER = 'FIPS State Code'
# Column in the CHR file that contains the County FIPS code for the current row
INPUT_COUNTY_HEADER = 'FIPS County Code'


# expects path to an accessible CSV file, return Path
def csv_path(value):
    path = pathlib.Path(value)
    if not path.is_file():
        raise argparse.ArgumentTypeError('File is missing or inaccessible')
    elif path.suffix.lower() != '.csv':
        raise argparse.ArgumentTypeError('File is not a CSV file')
    return path


# expects value to be a path to a directory, returns Path
def folder_path(value):
    path = pathlib.Path(value)
    if not path.is_dir():
        raise argparse.ArgumentTypeError('Path is not a directory!')
    return path


# expects 'INT:STRING', returns (int, str)
def column_spec(value):
    (column, sep, name) = value.partition(':')
    return (int(column), name)


def is_all_zero(fips):
    """
    Checks if a string is composed of all '0' characters.
    We use this to determine if a FIPS code refers to a state or national aggregate value.

    :param fips: a FIPS code
    :type fips: str
    :return: True of the string is all '0's, false otherwise
    :rtype: bool
    """
    try:
        # convert the FIPS string to an int; if it is all '0'
        # chars then the result will be equal to zero
        int_val = int(fips)
        return int_val == 0
    except:
        # definitely not all zeroes if it won't even parse as an integer
        return False


class MeasureOutput():
    """
    Encapsulates the task of reading one column from the CHR file and writing that columns
    values to a corresponding output file. Given an ID, name, and output directory, will
    read values from the column "measure_ID_value" in the CHR file, and write to a CSV file
    at "OUTPUT_DIR/(ID) LABEL.csv". The output CSV file should be compatible with our 2-fips
    upload format (separate State and County FIPS columns).

    """

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
        """
        Called once for each row in the input file. Extracts the value for a particular measure
        and write a new row to that measure's output file. Ignores a row if:
        * There is no value
        * The state fips is all zeroes (indicates a national aggregate)
        * The county fips is all zeroes (indicates a state aggregate)

        :param row: a row generated by a csv.dictreader
        :type row: dict
        """

        state_fips = row[INPUT_STATE_HEADER]
        county_fips = row[INPUT_COUNTY_HEADER]
        value = row[self.value_header]
        if value and not (is_all_zero(state_fips) or is_all_zero(county_fips)):
            to_write = {
                'State': state_fips,
                'County': county_fips,
                'Value': float(value)
            }
            self.writer.writerow(to_write)

    def finish(self):
        self.file.close()


def main():
    """
    Driver function. Parese command line arguments, creates measure output files for each
    column specified in the command line arguments, reads the input file, and cleans up.
    """

    parser = argparse.ArgumentParser(
        description='''Takes a CSV file downloaded from County Health Rankings and
        extracts specific columns, outputting a new CSV file for each extracted column.
        This can be used to generate a lot of uploadable files for the CHR Indicator
        Visualization Tool in one operation. Because the CHR CSV/SAS data is specified
        using numeric IDs, this requires you to specify the ID of the column to extract
        along with a name to associate with that column. The script will then extract values
        from the input file column with name 'measure_ID_value' and write them to a file
        that includes the corresponding name.
        ''',
        usage='%(prog)s PATH_TO_INPUT MEASURE_ID:LABEL MEASURE_ID:LABEL ...'
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
