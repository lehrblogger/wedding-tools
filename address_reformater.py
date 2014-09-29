#!/usr/bin/env python
# encoding: utf-8

from collections import OrderedDict
import csv
from optparse import OptionParser
import logging

minted_tuple_array = [
    ('Name',                        ['\xef\xbb\xbfSalutation', 'FirstName', 'LastName']),
    ('Street Address 1',            []),
    ('Street Address 2 (Optional)', ['HomeStreet']),
    ('City',                        ['HomeCity']),
    ('State/Region',                ['HomeState']),
    ('Country',                     ['HomeCountry']),
    ('Zip/Postal code',             ['HomePostalCode']),
    ('Email (Optional)',            [])
]
minted_mappings  = OrderedDict()
for minted_tuple in minted_tuple_array:
    minted_mappings[minted_tuple[0]] = minted_tuple[1]
    
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
            reader = csv.DictReader(csv_input, delimiter=',')
            def group_sorter(row):
                return row['Group']
            sorted_rows = sorted(reader, key=group_sorter, reverse=True)
            
            with open(self.output, 'w') as csv_output:
                writer = csv.DictWriter(csv_output, fieldnames=minted_mappings.keys())
                for sorted_row in sorted_rows:
                    row_to_write = {}
                    for mapped_key, mapped_val_list in minted_mappings.items():
                        columns_to_write = []
                        for mapped_val in mapped_val_list:
                            columns_to_write.append(sorted_row[mapped_val])
                        row_to_write[mapped_key] = ' '.join(columns_to_write)
                    writer.writerow(row_to_write)


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
