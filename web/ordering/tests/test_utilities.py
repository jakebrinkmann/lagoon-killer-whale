from django.test import TestCase
from ordering import utilities
from datetime import datetime

class DateFromDOYTestCase(TestCase):
    ''' Tests the utilities.date_from_doy function in the ordering app '''
       
    def test_normal_usage(self):
        date = datetime(2012, 1, 1)
        
        # date_from_doy takes a year and doy as args
        util_date = utilities.date_from_doy(2012, 1)
        self.assertEqual(date, util_date)
        
    def test_year_as_string(self):
        date = datetime(2012, 1, 1)
        util_date = utilities.date_from_doy('2012', 1)
        self.assertEqual(date, util_date)
        
    def test_doy_as_string(self):
        date = datetime(2012, 1, 1)
        util_date = utilities.date_from_doy(2012, '1')
        self.assertEqual(date, util_date)
        
    def test_both_as_string(self):
        date = datetime(2012, 1, 1)
        util_date = utilities.date_from_doy('2012', '1')
        self.assertEqual(date, util_date)
        
    def test_fail_zero_day(self):
        # should raise exception if day isn't in the given year
        self.assertRaises(Exception, utilities.date_from_doy, 2012, 0)
        
    def test_fail_400_day(self):
        # should raise exception if day isn't in the given year
        self.assertRaises(Exception, utilities.date_from_doy, 2012, 400)
        
    def test_fail_year_not_number(self):
        # should raise exception if year isn't a number
        self.assertRaises(ValueError, utilities.date_from_doy, 'asdfas', 400)
        
    def test_fail_doy_not_number(self):
        # should raise exception if doy isn't a number
        self.assertRaises(ValueError, utilities.date_from_doy, '2012', 'adsf')

        
class IsNumberTestCase(TestCase):
    ''' Tests is_number function '''
    
    def test_from_integer(self):
        self.assertTrue(utilities.is_number(1))
    
    def test_from_float(self):
        self.assertTrue(utilities.is_number(1.0))
        
    def test_fail_nonnumber(self):
        self.assertFalse(utilities.is_number('asdf'))