import unittest
import datetime

from unittest.mock import Mock, patch
from update_attendance import update_attendance
from freezegun import freeze_time


class UpdateAttendanceTest(unittest.TestCase):
    # this function is to test the function, mark_time_in in update_attendance/update_attendance.py
    def test_mark_time_in(self):
        # mock the function, get_current_week to always return week 9 without the loss of generality
        update_attendance.get_current_week = Mock(return_value=9)
        # mock the database cursor
        mock_database_cursor = Mock()

        student_id = "29821894"
        unit_code = "FIT3143_L1"
        cst = datetime.timedelta(hours=12, minutes=0, seconds=0)
        year = "2020"
        sem = "2"
        start_date = datetime.datetime(2020, 8, 3)

        # Class: FIT3143_L1
        # Class Start Time: 12:00:00 p.m.
        # Class duration: 2 hours / 7200 seconds long

        # Test case 1
        # Pass/Fail: Pass
        # Description: This test case is to test when the student marks his/her time in attendance at exactly 12:00:00 p.m sharp
        #               the student should be marked as not late
        with freeze_time("2020-10-12 12:00:00"):
            expected_output = False
            actual_output = update_attendance.mark_time_in(mock_database_cursor, student_id, unit_code, cst, year, sem, start_date)
            self.assertEqual(expected_output, actual_output)

        # Test case 2
        # Pass/Fail: Pass
        # Description: This test case is to test when the student marks his/her time in attendance at exactly 11:50:00 p.m,
        #               within 10 mins before the class starts
        #               the student should be marked as not late
        with freeze_time("2020-10-12 11:50:00"):
            expected_output = False
            actual_output = update_attendance.mark_time_in(mock_database_cursor, student_id, unit_code, cst, year, sem,
                                                           start_date)
            self.assertEqual(expected_output, actual_output)

        # Test case 3
        # Pass/Fail: Pass
        # Description: This test case is to test when the student marks his/her time in attendance at exactly 12:10:00 p.m,
        #               within 10 mins after the class starts
        #               the student should be marked as not late
        with freeze_time("2020-10-12 12:10:00"):
            expected_output = False
            actual_output = update_attendance.mark_time_in(mock_database_cursor, student_id, unit_code, cst, year, sem,
                                                           start_date)
            self.assertEqual(expected_output, actual_output)

        # Test case 4
        # Pass/Fail: Pass
        # Description: This test case is to test when the student marks his/her time in attendance at exactly 12:10:01 p.m,
        #               more than 10 mins after the class starts
        #               the student should be marked as late
        with freeze_time("2020-10-12 12:10:01"):
            expected_output = True
            actual_output = update_attendance.mark_time_in(mock_database_cursor, student_id, unit_code, cst, year, sem,
                                                           start_date)
            self.assertEqual(expected_output, actual_output)

    # the function is to test the function, mark_time_out in update_attendance/update_attendance.py
    def test_mark_time_out(self):
        # mock the function, get_current_week to always return week 9 without the loss of generality
        update_attendance.get_current_week = Mock(return_value=9)
        # mock the database cursor
        mock_database_cursor = Mock()

        # Class: FIT3143_L1
        # Class Start Time: 12:00:00 p.m.
        # Class duration: 1 hour / 3600 seconds long

        # Test case 1
        # Pass/Fail: Pass
        # Description: 1. This test case is to test if the student is able to mark time out (when the student leaves the class)
        #               when the total time elapsed is 1 seconds before 10 mins before the class is actually ended
        #               students can only start marking time out starting from 10 mins before the class is actually ended
        #              2.This test case is to test if the student is able to mark time out (when the student leaves the class)
        #               when time in has already been marked but time out is hasn't been marked yet
        student_id = "29821894"
        unit_code = "FIT3143_L1"
        year = "2020"
        sem = "2"
        start_date = datetime.datetime(2020, 8, 3)
        class_duration = 3600
        elapsed_time = 2999

        mock_database_cursor.fetchone.return_value = (
            "29821894",
            "FIT3143_L1",
            "9",
            "2020-10-12 12:00:00",
            None,
            False,
            "2020",
            "2"
        )

        expected_output = False
        actual_output = update_attendance.mark_time_out(mock_database_cursor, student_id, unit_code, year, sem,
                                                        start_date, class_duration, elapsed_time)
        self.assertEqual(expected_output, actual_output)

        # Test case 2
        # Pass/Fail: Pass
        # Description: 1.This test case is to test if the student is able to mark time out (when the student leaves the class)
        #               when the total time elapsed is 10 mins before the class is actually ended
        #               students can only start marking time out starting from 10 mins before the class is actually ended
        #              2.This test case is to test if the student is able to mark time out (when the student leaves the class)
        #               when time in has already been marked but time out is hasn't been marked yet
        student_id = "29821894"
        unit_code = "FIT3143_L1"
        year = "2020"
        sem = "2"
        start_date = datetime.datetime(2020, 8, 3)
        class_duration = 3600
        elapsed_time = 3000

        mock_database_cursor.fetchone.return_value = (
            "29821894",
            "FIT3143_L1",
            "9",
            "2020-10-12 12:00:00",
            None,
            False,
            "2020",
            "2"
        )

        expected_output = True
        actual_output = update_attendance.mark_time_out(mock_database_cursor, student_id, unit_code, year, sem, start_date, class_duration, elapsed_time)
        self.assertEqual(expected_output, actual_output)

        # Test case 3
        # Pass/Fail: Pass
        # Description: This test case is to test if the student is able to mark time out (when the student leaves the class)
        #               when the student has already marked time out, the time out field in the database is not empty
        mock_database_cursor.fetchone.return_value = (
            "29821894",
            "FIT3143_L1",
            "9",
            "2020-10-12 12:00:00",
            "2020-10-12 13:59:00",
            False,
            "2020",
            "2"
        )

        expected_output = False
        actual_output = update_attendance.mark_time_out(mock_database_cursor, student_id, unit_code, year, sem,
                                                        start_date, class_duration, elapsed_time)
        self.assertEqual(expected_output, actual_output)

        # Test case 4
        # Pass/Fail: Pass
        # Description: This test case is to test if the student is able to mark time out (when the student leaves the class)
        #               when the student has not marked time in for the current class yet, the current class attendance data
        #               of the student with student ID, {student ID} is not found on the database
        mock_database_cursor.fetchone.return_value = None

        expected_output = False
        actual_output = update_attendance.mark_time_out(mock_database_cursor, student_id, unit_code, year, sem,
                                                        start_date, class_duration, elapsed_time)
        self.assertEqual(expected_output, actual_output)


if __name__ == '__main__':
    unittest.main()

