import pymysql
from bokeh_server import skybright as sky
from datetime import datetime
import unittest


class TestSkyBrightDatabase(unittest.TestCase):
    """
    Test the Sky bright database
    """
    def setUp(self):
        """
        Setup a temporary table in the test database
        """
        config = sky.set_config()
        conn = pymysql.connect(**config)
        cursor = conn.cursor()

        # create a table
        cursor.execute("""CREATE TABLE IF NOT EXISTS SkyBrightness
                          (DATE_TIME datetime, SKYBRIGHTNESS float, SB_ERROR float,
                           MOON int, FILTER_BAND text, POSX int, TELESCOPE int, CLOUD_COVERAGE float)
                       """)
        conn.commit()

        # create and insert test data
        test_data = [['2012-01-01 12:11:00', 20.0, 20.1, 0, 0, "V", 0, 0.02],
                     ['2012-01-02 12:11:00', 21.0, 20.1, 1, 0, "V", 0, 0.02],
                     ['2012-01-03 12:11:00', 21.0, 20.1, 0, 1, "V", 0, 0.02],
                     ['2012-01-04 12:11:00', 21.0, 20.1, 0, 1, "V", 0, 0.02],
                     ['2012-01-05 12:11:00', 21.0, 20.1, 1, 1, "V", 0, 0.02],
                     ['2012-01-06 12:11:00', 21.0, 20.1, 0, 1, "B", 0, 0.02],
                     ['2012-01-07 12:11:00', 21.0, 20.1, 0, 1, "B", 0, 0.02],
                     ['2012-01-08 12:11:00', 21.0, 20.1, 0, 1, "B", 0, 0.02],
                     ['2012-01-09 11:11:00', 21.0, 20.1, 1, 1, "B", 0, 0.02],
                     ['2012-01-09 12:11:00', 21.0, 20.1, 0, 0, "B", 0, 0.02],
                     ['2012-01-10 12:11:00', 21.0, 20.1, 1, 0, "B", 0, 0.02],
                     ['2012-01-11 12:11:00', 21.0, 20.1, 0, 0, "B", 0, 0.02]
                     ]
        add_sb = ("INSERT INTO SkyBrightness "
                  "(DATE_TIME, SKYBRIGHTNESS, CLOUD_COVERAGE, MOON, TELESCOPE, FILTER_BAND, POSX, SB_ERROR)"
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
        config = sky.set_config()
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        cursor.executemany(add_sb, test_data)
        conn.commit()

        cursor.close()
        conn.close()

    def tearDown(self):
        """
        Delete the temporary table
        """
        config = sky.set_config()
        conn = pymysql.connect(**config)
        cursor = conn.cursor()

        cursor.execute('DROP TABLE IF EXISTS SkyBrightness; ')
        conn.commit()
        cursor.close()
        conn.close()

    def test_database_connection(self):
        print("Testing Connection")
        config = sky.set_config()
        conn = pymysql.connect(**config)
        conn.close()
        self.assertTrue(True)

    def test_skyBright_read_one(self):
        print("Testing single date read!")
        # DATE_TIME, SKYBRIGHTNESS, CLOUD_COVERAGE, MOON, TELESCOPE, FILTER_BAND, POSX, SB_ERROR

        # DATE_TIME,  SKYBRIGHTNESS, SB_ERROR, MOON, FILTER_BAND, POSX, TELESCOPE , CLOUD_COVERAGE
        actual = sky.read_database(datetime(2012, 1, 1), 1)
        expected = ((datetime(2012, 1, 1, 12, 11, 0), 20.0, 20.1, 0, 0, "V", 0, 0.02),)
        # 20.0, 0.01, 1, 'V', 0, 0, 20.0

        self.assertEqual(actual, expected)
        # 21.0, 0.02, 1, 'B', 0, 1, 20.0
        actual = sky.read_database(datetime(2012, 1, 7), 1)
        expected = ((datetime(2012, 1, 7, 12, 11, 0), 21.0, 20.1, 0, 1, "B", 0, 0.02),)


        self.assertEqual(actual, expected)

    def test_skyBright_read_seven(self):
        print("Testing single date read!")

        actual = sky.read_database(datetime(2012, 1, 9), 7)
        expected = ((datetime(2012, 1, 3, 12, 11, 0), 21.0, 20.1, 0, 1, "V", 0, 0.02),
                    (datetime(2012, 1, 4, 12, 11, 0), 21.0, 20.1, 0, 1, "V", 0, 0.02),
                    (datetime(2012, 1, 5, 12, 11, 0), 21.0, 20.1, 1, 1, "V", 0, 0.02),
                    (datetime(2012, 1, 6, 12, 11, 0), 21.0, 20.1, 0, 1, "B", 0, 0.02),
                    (datetime(2012, 1, 7, 12, 11, 0), 21.0, 20.1, 0, 1, "B", 0, 0.02),
                    (datetime(2012, 1, 8, 12, 11, 0), 21.0, 20.1, 0, 1, "B", 0, 0.02),
                    (datetime(2012, 1, 9, 11, 11, 0), 21.0, 20.1, 1, 1, "B", 0, 0.02),
                    (datetime(2012, 1, 9, 12, 11, 0), 21.0, 20.1, 0, 0, "B", 0, 0.02),)
        self.assertEqual(expected, actual)

        actual = sky.read_database(datetime(2012, 1, 8), 7)
        expected = ((datetime(2012, 1, 2, 12, 11, 0), 21.0, 20.1, 1, 0, "V", 0, 0.02),
                    (datetime(2012, 1, 3, 12, 11, 0), 21.0, 20.1, 0, 1, "V", 0, 0.02),
                    (datetime(2012, 1, 4, 12, 11, 0), 21.0, 20.1, 0, 1, "V", 0, 0.02),
                    (datetime(2012, 1, 5, 12, 11, 0), 21.0, 20.1, 1, 1, "V", 0, 0.02),
                    (datetime(2012, 1, 6, 12, 11, 0), 21.0, 20.1, 0, 1, "B", 0, 0.02),
                    (datetime(2012, 1, 7, 12, 11, 0), 21.0, 20.1, 0, 1, "B", 0, 0.02),
                    (datetime(2012, 1, 8, 12, 11, 0), 21.0, 20.1, 0, 1, "B", 0, 0.02),
                    (datetime(2012, 1, 9, 11, 11, 0), 21.0, 20.1, 1, 1, "B", 0, 0.02),)
        self.assertEqual(expected, actual)

    def test_skybright_read_range(self):
        print("Testing read range data")
        min_date = ["2012", "01", "01"]
        max_date = ["2012", "01", "12"]
        actual = sky.read_range_database(min_date, max_date)
        expected = ((datetime(2012, 1, 1, 12, 11, 0), 20.0, 20.1, 0, 0, "V", 0, 0.02),
                    (datetime(2012, 1, 2, 12, 11, 0), 21.0, 20.1, 1, 0, "V", 0, 0.02),
                    (datetime(2012, 1, 3, 12, 11, 0), 21.0, 20.1, 0, 1, "V", 0, 0.02),
                    (datetime(2012, 1, 4, 12, 11, 0), 21.0, 20.1, 0, 1, "V", 0, 0.02),
                    (datetime(2012, 1, 5, 12, 11, 0), 21.0, 20.1, 1, 1, "V", 0, 0.02),
                    (datetime(2012, 1, 6, 12, 11, 0), 21.0, 20.1, 0, 1, "B", 0, 0.02),
                    (datetime(2012, 1, 7, 12, 11, 0), 21.0, 20.1, 0, 1, "B", 0, 0.02),
                    (datetime(2012, 1, 8, 12, 11, 0), 21.0, 20.1, 0, 1, "B", 0, 0.02),
                    (datetime(2012, 1, 9, 11, 11, 0), 21.0, 20.1, 1, 1, "B", 0, 0.02),
                    (datetime(2012, 1, 9, 12, 11, 0), 21.0, 20.1, 0, 0, "B", 0, 0.02),
                    (datetime(2012, 1, 10, 12, 11, 0), 21.0, 20.1, 1, 0, "B", 0, 0.02),
                    (datetime(2012, 1, 11, 12, 11, 0), 21.0, 20.1, 0, 0, "B", 0, 0.02),
                    )
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
