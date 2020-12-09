import unittest
import datetime

from unittest.mock import Mock, patch
from update_attendance import update_attendance
from freezegun import freeze_time


class GetCurrentWeekTest(unittest.TestCase):
    # this function is to test the function, get_current_week in update_attendance/update_attendance.py
    def test_get_current_time(self):
        # mock the database cursor
        mock_database_cursor = Mock()
        mock_database_cursor.fetchone.return_value = (7,)
        start_date = datetime.datetime(2020, 8, 3)
        year = "2020"
        sem = "2"

        # Test case 1
        # Pass/Fail: Pass
        # Description: This test case is to test when the chosen date falls on the first week of the current semester
        with freeze_time("2020-08-06"):
            expected_output = 1
            actual_output = update_attendance.get_current_week(mock_database_cursor, start_date, year, sem)
            self.assertEqual(expected_output, actual_output)

        # Test case 2
        # Pass/Fail: Pass
        # Description: This test case is to test when the chosen date falls on the seventh week of the current semester
        with freeze_time("2020-09-17"):
            expected_output = 7
            actual_output = update_attendance.get_current_week(mock_database_cursor, start_date, year, sem)
            self.assertEqual(expected_output, actual_output)

        # Test case 3
        # Pass/Fail: Pass
        # Description: This test case is to test when the chosen date falls on the tenth week of the current semester
        # some might ask why the chosen date is week 10 instead of week 9 since if we're following the week schedule for
        # semester 2 of year 2020, this is supposed to be week 9
        # but please don't forget year 2020, sem 2 is a special case and we're following the standard that is used every sen
        # where the mid-sem break only lasts for a week
        with freeze_time("2020-10-15"):
            expected_output = 10
            actual_output = update_attendance.get_current_week(mock_database_cursor, start_date, year, sem)
            self.assertEqual(expected_output, actual_output)


if __name__ == '__main__':
    unittest.main()
