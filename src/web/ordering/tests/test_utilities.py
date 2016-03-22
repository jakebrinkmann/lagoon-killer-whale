from django.test import TestCase
from ordering import utilities
from datetime import datetime

class DateFromDOYTestCase(TestCase):
    ''' Tests the utilities.date_from_doy function in the ordering app '''

    def test_normal_usage(self):
        self.assertEqual(datetime(2012, 1, 1),
                         utilities.date_from_doy(2012, 1))

    def test_year_as_string(self):
        self.assertEqual(datetime(2012, 1, 1),
                         utilities.date_from_doy('2012', 1))

    def test_doy_as_string(self):
        self.assertEqual(datetime(2012, 1, 1),
                         utilities.date_from_doy(2012, '1'))

    def test_both_as_string(self):
        self.assertEqual(datetime(2012, 1, 1),
                         utilities.date_from_doy('2012', '1'))

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

    def test_last_good_day_leap_year(self):
        self.assertEqual(datetime(2012, 12, 31),
                         utilities.date_from_doy('2012', 366))

    def test_first_bad_day_leap_year(self):
        self.assertRaises(Exception, utilities.date_from_doy, 2012, 367)

    def test_last_good_day_nonleap_year(self):
        self.assertEqual(datetime(2011, 12, 31),
                         utilities.date_from_doy('2011', 365))

    def test_first_bad_day_nonleap_year(self):
        self.assertRaises(Exception, utilities.date_from_doy, 2011, 366)


class IsNumberTestCase(TestCase):
    ''' Tests is_number function '''

    def test_from_integer(self):
        self.assertTrue(utilities.is_number(1))

    def test_from_negative_integer(self):
        self.assertTrue(utilities.is_number(-1))

    def test_from_float(self):
        self.assertTrue(utilities.is_number(1.0))

    def test_from_negative_float(self):
        self.assertTrue(utilities.is_number(-1.0))

    def test_from_zero(self):
        self.assertTrue(utilities.is_number(0))

    def test_fail_nonnumber(self):
        self.assertFalse(utilities.is_number('asdf'))

    def test_fail_none(self):
        self.assertFalse(utilities.is_number(None))