import unittest

from unittest.mock import patch, Mock
from freezegun import freeze_time
from datetime import datetime, timedelta
from custom_functions import get_elapsed_time, set_current_weather, get_start_date


class CustomFunctionsTest(unittest.TestCase):
    # This function is to test the function, get_elapsed_time in custom_functions.py
    def test_get_elapsed_time(self):
        # Class: FIT3143_L1
        # Class Start Time: 12:00:00 p.m.
        # Class duration = 7200 (2 hours)

        # Test case 1
        # Pass/Fail: Pass
        # Description: This test case is to test the total time elapsed in seconds when the current time is 11:59:00 p.m.
        with freeze_time("2020-10-12 11:59:59"):
            cst = timedelta(hours=12, minutes=0, seconds=0)
            expected_output = 0
            actual_output = get_elapsed_time(cst)
            self.assertEqual(expected_output, actual_output)

        # Test case 2
        # Pass/Fail: Pass
        # Description: This test case is to test the total time elapsed in seconds when the current time is 12:00:00 p.m sharp.
        with freeze_time("2020-10-12 12:00:00"):
            cst = timedelta(hours=12, minutes=0, seconds=0)
            expected_output = 0
            actual_output = get_elapsed_time(cst)
            self.assertEqual(expected_output, actual_output)

        # Test case 3
        # Pass/Fail: Pass
        # Description: This test case is to test the total time elapsed in seconds when the current time is 12:00:01 p.m,
        #               a second afer the current class start time
        with freeze_time("2020-10-12 12:00:01"):
            cst = timedelta(hours=12, minutes=0, seconds=0)
            expected_output = 1
            actual_output = get_elapsed_time(cst)
            self.assertEqual(expected_output, actual_output)

        # Test case 4
        # Pass/Fail: Pass
        # Description: This test case is to test the total time elapsed in seconds when the current time is 12:01:00 p.m,
        #               a minute afer the current class start time
        with freeze_time("2020-10-12 12:01:00"):
            cst = timedelta(hours=12, minutes=0, seconds=0)
            expected_output = 60
            actual_output = get_elapsed_time(cst)
            self.assertEqual(expected_output, actual_output)

    # this function is to test the function, get_start_date in the custom_functions.py
    def test_get_start_date(self):
        # mock Database Cursor
        mock_database_cursor = Mock()

        # Test case 1
        # Pass/Fail: Pass
        # Description: This test case is to test if the function is able to return the correct start date retrieved
        #               from the database
        #               since database is a third-party dependency and is not suitable to be included in the unit testing,
        #               we are using mock to mock the returned value from the database
        mock_database_cursor.fetchall.return_value = [("2020-08-03",)]
        year = "2020"
        sem = "2"
        expected_output = datetime(2020, 8, 3)
        actual_output = get_start_date(mock_database_cursor, year, sem)

    # mocking the third party library, pyowm for retrieving the weather status of KUALA LUMPUR, MALAYSIA
    @patch('custom_functions.pyowm')
    # this function is to test the function, set_current_weather in custom_functions.py
    def test_set_current_weather(self, mock_pyowm):
        mock_pyowm.OWM.return_value.weather_at_place.return_value.get_weather.return_value.get_status.return_value = "Clear"

        mock_database_cursor = Mock()
        unit_code = "FIT2107_L1"
        year = "2020"
        sem = "2"
        week = "9"
        status = "Clear"
        cst = timedelta(hours=13, minutes=0, seconds=0)

        set_current_weather(mock_database_cursor, unit_code, year, sem, week, cst)

        query = "INSERT " \
                "INTO " \
                "WEATHER " \
                "(" \
                "UNIT_CODE, " \
                "YEAR, " \
                "SEMESTER, " \
                "WEEK, " \
                "CLASS_DATETIME, " \
                "WEATHER" \
                ") " \
                "VALUES " \
                "(" \
                "'{}', '{}', '{}', '{}', '{}', '{}'" \
                ")".format(unit_code, year, sem, week, cst, status)
        # make sure the function is executing the query with the specified arguments passed to the function
        # and the weather status using web API.
        mock_database_cursor.execute.assert_called_with(query)
        

if __name__ == '__main__':
    unittest.main()
