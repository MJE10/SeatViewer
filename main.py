import argparse

import argparse
import os.path

# Initialize parser
parser = argparse.ArgumentParser(description='Parses a csv file from the seats experiment.')

parser.add_argument("input_file", help="The input file to parse.")

args = parser.parse_args()

# check if the input file exists and is readable
if not os.path.exists(args.input_file):
    print("Input file does not exist.")
    exit(1)
if not os.access(args.input_file, os.R_OK):
    print("Input file is not readable.")
    exit(1)

# get the list of sui's from the input csv file
sui_list = []
with open(args.input_file, 'r') as f:
    for line in f:
        sui = line.split(',')[0]
        if sui not in sui_list and sui != "clinical.sui":
            sui_list.append(sui)

print(sui_list)