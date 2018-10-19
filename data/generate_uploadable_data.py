import csv
import os
import random

COUNTY_FILE_NAME = "counties_and_equivalents_2010.csv"
YEARS_TO_GENERATE = (2016, 2017, 2018,)

HEADERS = ('STATE_USPS', 'STATE_FIPS', 'FIPS', 'NAME', 'Value',)

MU = 0.5
SIGMA = 0.1

def read_rows(file):
    rows = []
    headers= []
    reader = csv.DictReader(file)

    for row in reader:
        if not headers:
            headers = [h for h in row.keys()]
        rows.append(row)

    return (headers, rows)

def main():
    input_path = os.path.join('.', COUNTY_FILE_NAME)

    with open(input_path, 'r', newline='') as csv_in:
        (_, county_rows) = read_rows(csv_in)

        for year in YEARS_TO_GENERATE:
            output_path = os.path.join('.', f'sample_{year}.csv')
            with open(output_path, 'w', newline='') as csv_out:

                writer = csv.DictWriter(csv_out, fieldnames=HEADERS, extrasaction='ignore', quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()

                for county in county_rows:
                    gaussian_float = random.gauss(MU, SIGMA)
                    shifted = round(gaussian_float * 1000)
                    int_value = int(shifted)
                    county['Value'] = int_value
                    writer.writerow(county)

main()
