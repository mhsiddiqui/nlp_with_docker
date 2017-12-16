import csv
import re

import collections

from tts.text_processor import RESOURCE_PATH


class GetStringType(object):
    """
    Get String type if it is Date, Time, Number

    Number formats which are handled are below

        1. Date (12.12.12 or 12/12/12 or 12-12-12)
        2. Time (12:12:12 or 12:12)
        3. Number (12 or 12.12)

    """

    def __init__(self, text):
        self.text = text

    def get_string_type(self):
        if bool(self._date_strings()):
            return 'Date'
        elif bool(self._time_strings()):
            return 'Time'
        elif bool(self._number_strings()):
            return 'Number'
        else:
            return 'None'

    def _get_all_months(self):
        mapping_dict = {}
        with open(RESOURCE_PATH + '/month.csv', 'rb') as f:
            mappings = csv.reader(f)
            for row in mappings:
                mapping_dict.update({row[0]: row[1]})
        return set(mapping_dict.values())

    def _date_strings(self):
        regex_string = '\d{1,4}[./-]\d{1,4}[./-]\d{1,4}'
        regex = re.compile(regex_string)
        find_string = regex.findall(self.text)
        self.text = re.sub(regex_string, '', self.text)
        find_string += self._text_date()
        return find_string

    def _text_date(self):
        all_months = self._get_all_months()
        text_dates = []
        regex_pattern = '%s \d{4}'
        for month in all_months:
            comp_regex = regex_pattern % month.decode('utf-8').replace(' ', '')
            regex = re.compile(comp_regex)
            find_string = regex.findall(self.text)
            if bool(find_string):
                text_dates += find_string
                self.text = re.sub(comp_regex, '', self.text)
        return text_dates

    def _time_strings(self):
        regex_string = '\d{1,2}:\d{1,2}(?::\d{1,2})?'
        regex = re.compile(regex_string)
        find_string = regex.findall(self.text)
        self.text = re.sub(regex_string, '', self.text)
        return find_string

    def _number_strings(self):
        regex = re.compile('(\d+(?:\.\d+)?)')
        return regex.findall(self.text)


class NumberStrings(GetStringType):
    """
    Get all number strings in a string.

    Number formats which are handled are below

        1. Date (12.12.12 or 12/12/12 or 12-12-12)
        2. Time (12:12:12 or 12:12)
        3. Number (12 or 12.12)
    """

    def __init__(self, text, all_types=True, date_only=False, time_only=False, number_only=False):
        self.text = text
        self.all_types = all_types
        self.date_only = date_only
        self.time_only = time_only
        self.number_only = number_only
        super(NumberStrings, self).__init__(text)

    def get_number_strings(self):
        output = collections.OrderedDict()
        if self.all_types:
            output.update({'date': self._date_strings()})
            output.update({'time': self._time_strings()})
            output.update({'number': self._number_strings()})
        else:
            if self.date_only:
                output.update({
                    'date': self._date_strings()
                })
            if self.time_only:
                output.update({
                    'time': self._time_strings()
                })
            if self.number_only:
                output.update({
                    'number': self._number_strings()
                })
        return output
