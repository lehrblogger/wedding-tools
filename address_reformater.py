#!/usr/bin/env python
# encoding: utf-8

import csv
import logging
from collections import OrderedDict
from optparse import OptionParser
import re

temp_concat_string = ' & '

class Member:
    
    def __init__(self, prefix, first, last, nick=None):
        self.prefix = prefix
        self.first  = first
        self.nick   = nick
        self.last   = last
        
    def full_name(self):
        if self.nick:
            return self.prefix + self.first + ' "' + self.nick + '" ' + self.last
        return     self.prefix + self.first + ' '                 ' ' + self.last
        
    def __eq__(self, other):
        return isinstance(other, Member) and \
            self.prefix == other.prefix  and \
            self.first  == other.first   and \
            self.nick   == other.nick    and \
            self.last   == other.last
    
    def __hash__(self):
        return hash((self.prefix, self.first, self.nick, self.last))

class Address:
    
    def __init__(self, street_1, city, state_region, zip_postal, country):
        self.street_1     = street_1
        self.city         = city
        self.state_region = state_region
        self.zip_postal   = zip_postal
        self.country      = country
    
    def __str__(self):
        return self.street_1 + ', ' + self.city + ', ' + self.state_region + ' ' + self.zip_postal

class Group:
    
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self._members = set()
    
    @staticmethod
    def fieldnames(format='minted'):
        if format == 'minted':
            return [
                'Name'                       ,
                'Street Address 1'           ,
                'Street Address 2 (Optional)',
                'City'                       ,
                'State/Region'               ,
                'Country'                    ,
                'Zip/Postal code'            ,
                'Email (Optional)'
            ]
        else:
            return []
    
    def add_member(self, member):
        self._members.add(member)
        
    def name_first_line(self):
        return self.name.split(temp_concat_string)[0]
    
    def name_second_line(self):
        if temp_concat_string in self.name:
            return self.name.split(temp_concat_string)[1]
    
    def row(self, format='minted'):
        if format == 'minted':
            return {
                'Name'                       : self.name_first_line(),
                'Street Address 1'           : self.name_second_line() if self.name_second_line() else self.address.street_1,
                'Street Address 2 (Optional)': self.name_second_line() if self.address.street_1   else None,
                'City'                       : self.address.city,
                'State/Region'               : self.address.state_region,
                'Country'                    : self.address.country,
                'Zip/Postal code'            : self.address.zip_postal,
                'Email (Optional)'           : None
            }
        else:
            return {}
    
    def __str__(self):
        return str(self._members) + ' ' + str(self.address)
        

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
                groups = {}
                
                reader = csv.DictReader(csv_input, delimiter=',')
                sorted_rows = sorted(reader, key=lambda x: (x['HomeStreet']), reverse=True)  # make groups with addresses first
                for row in sorted_rows:
                    first, nick = re.match('^(.*)\ ?\"?(.*)\"?$', row['FirstName']).groups()
                    member = Member(row['\xef\xbb\xbfSalutation'], first, row['LastName'], nick)
                    
                    group_name = row['Group'].replace('\\n', temp_concat_string)
                    if (group_name not in groups):
                        address = Address(row['HomeStreet'], row['HomeCity'], row['HomeState'], row['HomePostalCode'], row['HomeCountry'])
                        group = Group(group_name, address)
                        groups[group_name] = group
                    groups[group_name].add_member(member)
                
                writer = csv.DictWriter(csv_output, fieldnames=Group.fieldnames())
                header_row = {}
                for fieldname in writer.fieldnames:
                    header_row[fieldname] = fieldname
                writer.writerow(header_row)
                for group_name, group in groups.items():
                    writer.writerow(group.row())
                    
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
