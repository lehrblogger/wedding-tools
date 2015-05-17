#!/usr/bin/env python
# encoding: utf-8

import csv
import logging
from collections import OrderedDict
from optparse import OptionParser
import re

temp_concat_string = ' & '

class Guest:
    
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
        return isinstance(other, Guest) and \
            self.prefix == other.prefix  and \
            self.first  == other.first   and \
            self.nick   == other.nick    and \
            self.last   == other.last
    
    def __hash__(self):
        return hash((self.prefix, self.first, self.nick, self.last))
    

class Address:
    
    def __init__(self, street, city, state_region, zip_postal, country):
        street_1 = street
        street_2 = None
        if '\n' in street:
            street_1, street_2 = street.split('\n')
        self.street_1     = street_1
        self.street_2     = street_2
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
        self._guests = set()
    
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
    
    def add_guest(self, guest):
        self._guests.add(guest)
    
    def name_first_line(self):
        return self.name.split(temp_concat_string)[0]
    
    def name_second_line(self):
        if temp_concat_string in self.name:
            return self.name.split(temp_concat_string)[1]
    
    def row(self, format='minted'):
        if format == 'minted':
            if not self.address.street_1:
                print '  Skipping row for ' + self.name + ': no address'
                return {}
            if self.name_second_line() and self.address.street_2:
                print '  Skipping row for ' + self.name + ': too many lines'
                return {}
            return {
                'Name'                       : self.name_first_line(),
                'Street Address 1'           : self.name_second_line() if self.name_second_line() else self.address.street_1,
                'Street Address 2 (Optional)': self.address.street_1   if self.name_second_line() else self.address.street_2,
                'City'                       : self.address.city,
                'State/Region'               : self.address.state_region,
                'Country'                    : self.address.country,
                'Zip/Postal code'            : self.address.zip_postal,
                'Email (Optional)'           : None
            }
        else:
            return {}
    
    def __str__(self):
        return str(self._guests) + ' ' + str(self.address)
    

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
                for row in reader:
                    first, nick = re.match('^(.*)\ ?\"?(.*)\"?$', row['FirstName']).groups()
                    guest = Guest(row['\xef\xbb\xbfSalutation'], first, row['LastName'], nick)
                    
                    group_name = row['Organisation'].replace('\\n', temp_concat_string)  # 'Organisation' with an 's'
                    if group_name:
                        if (group_name not in groups):
                            address = Address(row['LinkedOrganizationPostalStreet'],
                                              row['LinkedOrganizationPostalCity'],
                                              row['LinkedOrganizationPostalState'],
                                              row['LinkedOrganizationPostalCode'],
                                              row['LinkedOrganizationPostalCountry'])
                            group = Group(group_name, address)
                            groups[group_name] = group
                        groups[group_name].add_guest(guest)
                    else:
                        print '  Skipping row for ' + guest.full_name() + ': no group'
                
                writer = csv.DictWriter(csv_output, fieldnames=Group.fieldnames())
                header_row = {}
                for fieldname in writer.fieldnames:
                    header_row[fieldname] = fieldname
                writer.writerow(header_row)
                for group_name, group in groups.items():
                    if group.row():
                        writer.writerow(group.row())
    

def main():
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input",
                    help="the file from which you want to read the data")
    parser.add_option("-o", "--output", dest="output",
                    help="the file to which you want to write the data")
    parser.add_option("-d", "--debug", dest="debug",
                    help="print extra debugging information",
                    action='store_const', const=True, default=False)
    (options, args) = parser.parse_args()
    if options.input and options.output:
        address_reformater = AddressReformater(options.input, options.output, debug=options.debug)
        address_reformater.run()

if __name__ == '__main__':
    main()
