#!/usr/bin/env python
# encoding: utf-8

import csv
import logging
from collections import OrderedDict
from optparse import OptionParser

class AddressReformater:

    def __init__(self, input, output, debug=False):
        self.input = input
        self.output = output
        self.debug = debug

    def run(self):
        if self.debug:
            print 'Input:  ' + self.input;
            print 'Output: ' + self.output;
        with open(self.input, 'r') as csv_input:
            with open(self.output, 'w') as csv_output:
                
                # Read the rows, then sort by group and then street address
                reader = csv.DictReader(csv_input, delimiter=',')
                sorted_rows = sorted(reader, key=lambda x: (x['Group'], x['HomeStreet']), reverse=True)

                # Filter the rows to have one per Group
                filtered_sorted_rows = []
                current_group = ''
                for sorted_row in sorted_rows:
                    if (current_group != sorted_row['Group']):
                        current_group = sorted_row['Group']
                        filtered_sorted_rows.append(sorted_row)
                sorted_rows = filtered_sorted_rows

                # Set up the mappings, although note special case below for newlines in the Group
                minted_tuple_array = [
                    ('Name',                        'Group'),
                    ('Street Address 1',            None),
                    ('Street Address 2 (Optional)', 'HomeStreet'),
                    ('City',                        'HomeCity'),
                    ('State/Region',                'HomeState'),
                    ('Country',                     'HomeCountry'),
                    ('Zip/Postal code',             'HomePostalCode'),
                    ('Email (Optional)',            None)
                ]
                minted_mappings  = OrderedDict()
                for minted_tuple in minted_tuple_array:
                    minted_mappings[minted_tuple[0]] = minted_tuple[1]

                # Prepare the writer and re-add the header
                writer = csv.DictWriter(csv_output, fieldnames=minted_mappings.keys())
                header_row = {}
                for fieldname in writer.fieldnames:
                    header_row[fieldname] = fieldname
                writer.writerow(header_row)

                # Then Loop through and add a row for each Group
                for sorted_row in sorted_rows:
                    row_to_write = {}
                    for mapped_key, mapped_val in minted_mappings.items():
                        if mapped_val:
                            # Split the Group into new lines and move as needed.
                            if mapped_val == 'Group' and '\\n' in sorted_row[mapped_val]:
                                name_rows = sorted_row[mapped_val].split('\\n')
                                if (len(name_rows)) > 2: raise Exception
                                row_to_write[mapped_key]         = name_rows[0]
                                row_to_write['Street Address 1'] = name_rows[1]
                            #TODO move up the second street address line to be first if we have a one-line Group
                            else:
                                row_to_write[mapped_key] = sorted_row[mapped_val]
                    writer.writerow(row_to_write)
                
                # Clean up
                csv_input.close()
                csv_output.close()


def main():
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input",
                    help="the file from which you want to read the data")
    parser.add_option("-o", "--output", dest="output",
                    help="the file to which you want to write the data")
    parser.add_option("-d", "--debug", dest="debug",
                    help="limit the number of threads fetched for debugging",
                    action='store_const', const=True, default=False)
    (options, args) = parser.parse_args()
    if options.input and options.output:
        address_reformater = AddressReformater(options.input, options.output, debug=options.debug)
        address_reformater.run()

if __name__ == '__main__':
    main()
