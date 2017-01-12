from bokeh_server import skybright as sb
import unittest
from datetime import datetime, timedelta


class TestSkybright(unittest.TestCase):
    """
        Testing the feature and functions of skybright
    """
    def test_find_filter_number(self):
        """
            Testing for the correct representing number for a given filter can be found
        """
        result = sb.find_filter_number("V")
        self.assertEqual(result, 0)
        result = sb.find_filter_number("B")
        self.assertEqual(result, 1)
        result = sb.find_filter_number("R")
        self.assertEqual(result, 2)
        result = sb.find_filter_number("I")
        self.assertEqual(result, 3)
        result = sb.find_filter_number("F")
        self.assertEqual(result, -1)

    def test_find_filter_name(self):
        """
            Testing for the correct representing filter for a given number can be found
        """
        result = sb.find_filter_name(0)
        self.assertEqual(result, "V")
        result = sb.find_filter_name(1)
        self.assertEqual(result, "B")
        result = sb.find_filter_name(2)
        self.assertEqual(result, "R")
        result = sb.find_filter_name(3)
        self.assertEqual(result, "I")
        result = sb.find_filter_name(4)
        self.assertEqual(result, None)
        result = sb.find_filter_name(65)
        self.assertEqual(result, None)
        result = sb.find_filter_name(-1)
        self.assertEqual(result, None)

    def test_find_position(self):
        """
            Testing the given number represent the right position
        """
        result = sb.find_position(0)
        self.assertEqual(result, "Zenith")
        result = sb.find_position(1)
        self.assertEqual(result, "South")
        result = sb.find_position(2)
        self.assertEqual(result, "East")
        result = sb.find_position(3)
        self.assertEqual(result, "North")
        result = sb.find_position(4)
        self.assertEqual(result, "West")
        result = sb.find_position(-1)
        self.assertEqual(result, None)
        result = sb.find_position(45)
        self.assertEqual(result, None)

    def test_find_tittle(self):
        """
            Testing to correct tittle for the given position number
        """
        result = sb.find_tittle(0)
        self.assertEqual(result, 'Zenith')
        result = sb.find_tittle(1)
        self.assertEqual(result, 'South')
        result = sb.find_tittle(2)
        self.assertEqual(result, 'East')
        result = sb.find_tittle(3)
        self.assertEqual(result, 'North')
        result = sb.find_tittle(4)
        self.assertEqual(result, 'West')
        result = sb.find_tittle(5)
        self.assertEqual(result, None)
        result = sb.find_tittle(45)
        self.assertEqual(result, None)

    def test_find_telescope_name(self):
        """
            Testing if the telescope corresponding number represent the right telescope name
        """
        result = sb.find_telescope_name(0)
        self.assertEqual(result, "Sunrise")
        result = sb.find_telescope_name(1)
        self.assertEqual(result, "Sunset")
        result = sb.find_telescope_name(2)
        self.assertEqual(result, None)
        result = sb.find_telescope_name("0")
        self.assertEqual(result, None)

    def test_find_range_date(self):
        """
            Testing if data between times after 00:00:00 and before 12:00:00 belong to the night before data
        """
        t1 = datetime.strptime("2016-03-12 00:16:13", "%Y-%m-%d %H:%M:%S")
        t2 = datetime.strptime("2016-03-12 10:16:13", "%Y-%m-%d %H:%M:%S")
        t3 = datetime.strptime("2016-03-12 22:16:13", "%Y-%m-%d %H:%M:%S")
        result = sb.find_range_date(t1)
        self.assertEqual(result, datetime.strptime("2016-03-11", "%Y-%m-%d").date())
        result = sb.find_range_date(t2)
        self.assertEqual(result, datetime.strptime("2016-03-11", "%Y-%m-%d").date())
        result = sb.find_range_date(t3)
        self.assertEqual(result, datetime.strptime("2016-03-12", "%Y-%m-%d").date())

    def test_find_index(self):
        """
            Testing the correct index of a value in a list
        """
        result = sb.find_value_index("bar", ["foo", "bar", "baz"])
        self.assertEqual(result, 1)
        result = sb.find_value_index("bar", ["foo", "fax", "tar", "bar", "baz"])
        self.assertEqual(result, 3)
        result = sb.find_value_index("baz", ["foo", "fax", "tar", "bar", "baz"])
        self.assertEqual(result, 4)
        result = sb.find_value_index("foo", ["foo", "fax", "tar", "bar", "baz"])
        self.assertEqual(result, 0)
        result = sb.find_value_index("barz", ["foo", "fax", "tar", "bar", "baz"])
        self.assertEqual(result, -1)

    def test_selector_to_date(self):
        """
            Testing if I will always get a date from what is selected bu the selector
        """
        result = sb.selector_to_date(2016, 12, 13)
        self.assertEqual(result, datetime(2016, 12, 13))
        result = sb.selector_to_date('2016', '12', '13')
        self.assertEqual(result, datetime(2016, 12, 13))

    def test_this(self):
        """
            Testing
        """
        result = 1
        self.assertEqual(result, 1)

if __name__ == '__main__':
    unittest.main()
