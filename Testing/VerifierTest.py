import unittest
import datetime

from unittest.mock import Mock
from verif import verifier


class VerifierTest(unittest.TestCase):

    # this function is to test the function, get_student_id in verif/verifier.py
    def test_get_student_id(self):
        # mock database cursor
        mock_database_cursor = Mock()

        # Test case 1
        # Pass/Fail: Pass
        # Description: This test case is to test when the UID of the student card is tie to a student ID in the database
        uid = "1a2b3c4d"
        mock_database_cursor.fetchone.return_value = ("29821894",)
        expected_output = "29821894"
        actual_output = verifier.get_student_id(mock_database_cursor, uid)
        self.assertEqual(expected_output, actual_output)

        # Test case 2
        # Pass/Fail: Pass
        # Description: This test case is to test when the UID of the student card doesn't exist in the database
        mock_database_cursor.fetchone.return_value = None
        expected_output = ""
        actual_output = verifier.get_student_id(mock_database_cursor, uid)
        self.assertEqual(expected_output, actual_output)

    # this function is to test the function, is_student in verif/verifier.py
    def test_is_student(self):
        # mock database cursor
        mock_database_cursor = Mock()

        # Test case 1
        # Pass/Fail: Pass
        # Description: This test case is to test when the student ID exists in the database
        student_id = "29821894"
        mock_database_cursor.fetchall.return_value = [
            (
                "29821894",
                "Zu Wei",
                "Liew",
                "1998-06-06",
                "zuwei@student.monash.edu",
                "password"
            )
        ]
        expected_output = True
        actual_output = verifier.is_student(mock_database_cursor, student_id)
        self.assertEqual(expected_output, actual_output)

        # Test case 2
        # Pass/Fail: Pass
        # Description: This test case is to test when the student ID doesn't exist in the database
        mock_database_cursor.fetchall.return_value = []
        expected_output = False
        actual_output = verifier.is_student(mock_database_cursor, student_id)
        self.assertEqual(expected_output, actual_output)

    # this function is to test the function, get_curr_class in verif/verifier.py
    def test_get_curr_class(self):
        # mock database cursor
        mock_database_cursor = Mock()
        # Test case 1
        # Pass/Fail: Pass
        # Description: This test case is to test when the time difference between the current class start time
        # and the current time is 0 seconds
        mock_database_cursor.fetchall.return_value = [
            (
                "FIT2107_L1",
                datetime.time(hour=13, minute=0, second=0),
                "3600"
            )
        ]

        room_id = "CS001"
        day = "Tuesday"
        curr_time = datetime.timedelta(hours=13, minutes=0, seconds=0)
        last_class = "FIT3155_L1"

        expected_output = ("FIT2107_L1", datetime.time(hour=13, minute=0, second=0), "3600")
        actual_output = verifier.get_curr_class(mock_database_cursor, room_id, day, curr_time, last_class)
        self.assertEqual(expected_output, actual_output)

        # Test case 2
        # Pass/Fail: Pass
        # Description: This test case is to test when the time difference between the current class start time
        # and the current time is -10 minutes / -600 seconds
        # the current time is 10 minutes earlier than the current class start time
        # the algorithm will only consider the class as the current class when the time difference with the current time is less than or equal 10 minutes
        mock_database_cursor.fetchall.return_value = [
            (
                "FIT2107_L1",
                datetime.time(hour=13, minute=0, second=0),
                "3600"
            )
        ]

        room_id = "CS001"
        day = "Tuesday"
        curr_time = datetime.timedelta(hours=12, minutes=50, seconds=0)
        last_class = "FIT3155_L1"

        expected_output = ("FIT2107_L1", datetime.time(hour=13, minute=0, second=0), "3600")
        actual_output = verifier.get_curr_class(mock_database_cursor, room_id, day, curr_time, last_class)
        self.assertEqual(expected_output, actual_output)

        # Test case 3
        # Pass/Fail: Pass
        # Description: This test case is to test when the time difference between the current class start time
        # and the current time is 10 minutes / 600 seconds
        # the current time is 10 minutes after than the current class start time
        # the algorithm will only consider the class as the current class when the time difference with the current time is less than or equal 10 minutes
        mock_database_cursor.fetchall.return_value = [
            (
                "FIT2107_L1",
                datetime.time(hour=13, minute=0, second=0),
                "3600"
            )
        ]

        room_id = "CS001"
        day = "Tuesday"
        curr_time = datetime.timedelta(hours=13, minutes=10, seconds=0)
        last_class = "FIT3155_L1"

        expected_output = ("FIT2107_L1", datetime.time(hour=13, minute=0, second=0), "3600")
        actual_output = verifier.get_curr_class(mock_database_cursor, room_id, day, curr_time, last_class)
        self.assertEqual(expected_output, actual_output)

        # Test case 4
        # Pass/Fail: Pass
        # Description: This test case is to test when the time difference between the current class start time
        # and the current time is more than 10 minutes / 600 seconds
        # the current time is more than 10 minutes earlier than the current class start time
        # the algorithm will only consider the class as the current class when the time difference with the current time is less than or equal 10 minutes
        mock_database_cursor.fetchall.return_value = [
            (
                "FIT2107_L1",
                datetime.time(hour=13, minute=0, second=0),
                "3600"
            )
        ]

        room_id = "CS001"
        day = "Tuesday"
        curr_time = datetime.timedelta(hours=12, minutes=49, seconds=59)
        last_class = "FIT3155_L1"

        expected_output = 0
        actual_output = verifier.get_curr_class(mock_database_cursor, room_id, day, curr_time, last_class)
        self.assertEqual(expected_output, actual_output)

        # Test case 5
        # Pass/Fail: Pass
        # Description: This test case is to test when the time difference between the current class start time
        # and the current time is more than 10 minutes / 600 seconds
        # the current time is more than 10 minutes later than the current class start time
        # the algorithm will only consider the class as the current class when the time difference with the current time is less than or equal 10 minutes
        mock_database_cursor.fetchall.return_value = [
            (
                "FIT2107_L1",
                datetime.time(hour=13, minute=0, second=0),
                "3600"
            )
        ]

        room_id = "CS001"
        day = "Tuesday"
        curr_time = datetime.timedelta(hours=13, minutes=10, seconds=1)
        last_class = "FIT3155_L1"

        expected_output = 0
        actual_output = verifier.get_curr_class(mock_database_cursor, room_id, day, curr_time, last_class)
        self.assertEqual(expected_output, actual_output)

        # Test case 6
        # Pass/Fail: Pass
        # Description: This test case is to test when no class will happen in the classroom for a particular day (ex. Monday, Tuesday, Wednesday,...)
        mock_database_cursor.fetchall.return_value = []

        room_id = "CS001"
        day = "Tuesday"
        curr_time = datetime.timedelta(hours=13, minutes=0, seconds=0)
        last_class = "FIT3155_L1"

        expected_output = 0
        actual_output = verifier.get_curr_class(mock_database_cursor, room_id, day, curr_time, last_class)
        self.assertEqual(expected_output, actual_output)

        # Test case 7
        # Pass/Fail: Pass
        # Description: This test case is to test when the time difference between the current class start time
        # and the current time is 0 seconds but there was a class happenned right BEFORE the current class
        mock_database_cursor.fetchall.return_value = [
            (
                "FIT3155_L1",
                datetime.time(hour=12, minute=0, second=0),
                "3600"
            ),
            (
                "FIT2107_L1",
                datetime.time(hour=13, minute=0, second=0),
                "3600"
            )
        ]

        room_id = "CS001"
        day = "Tuesday"
        curr_time = datetime.timedelta(hours=13, minutes=0, seconds=0)
        last_class = "FIT3155_L1"

        expected_output = ("FIT2107_L1", datetime.time(hour=13, minute=0, second=0), "3600")
        actual_output = verifier.get_curr_class(mock_database_cursor, room_id, day, curr_time, last_class)
        self.assertEqual(expected_output, actual_output)

        # Test case 8
        # Pass/Fail: Pass
        # Description: This test case is to test when the time difference between the current class start time
        # and the current time is 0 seconds but a class will happen right AFTER the current class
        mock_database_cursor.fetchall.return_value = [
            (
                "FIT2107_L1",
                datetime.time(hour=13, minute=0, second=0),
                "3600"
            ),
            (
                "FIT3155_L1",
                datetime.time(hour=14, minute=0, second=0),
                "3600"
            )
        ]

        room_id = "CS001"
        day = "Tuesday"
        curr_time = datetime.timedelta(hours=13, minutes=0, seconds=0)
        last_class = "FIT3155_L1"

        expected_output = ("FIT2107_L1", datetime.time(hour=13, minute=0, second=0), "3600")
        actual_output = verifier.get_curr_class(mock_database_cursor, room_id, day, curr_time, last_class)
        self.assertEqual(expected_output, actual_output)

    # this function is to test the function, in_right_class in verif/verifier.py
    def test_in_right_class(self):
        # mock database cursor
        mock_database_cursor = Mock()
        # Test case 1
        # Pass/Fail: Pass
        # Description: This test case is to test when the student is taking the class that is happening right now
        # in the classroom in the current semester
        mock_database_cursor.fetchall.return_value = [
            ("FIT3155_L1",),
            ("FIT2107_L1",)
        ]

        student_id = "29821894"
        year = "2020"
        sem = "2"
        curr_class = "FIT2107_L1"

        expected_output = True
        actual_output = verifier.in_right_class(mock_database_cursor, student_id, year, sem, curr_class)
        self.assertEqual(expected_output, actual_output)

        # Test case 2
        # Pass/Fail: Pass
        # Description: This test case is to test when the student is not taking the class that is happening right now
        # in the classroom in the current semester
        mock_database_cursor.fetchall.return_value = [
            ("FIT3155_L1",),
            ("FIT2107_L1,",)
        ]

        student_id = "29821894"
        year = "2020"
        sem = "2"
        curr_class = "FIT3143_L1"

        expected_output = False
        actual_output = verifier.in_right_class(mock_database_cursor, student_id, year, sem, curr_class)
        self.assertEqual(expected_output, actual_output)


if __name__ == '__main__':
    unittest.main()

