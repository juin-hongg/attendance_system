import math

from my_logging import my_logging
from datetime import datetime, timedelta

logger = my_logging.get_logger(__name__)


def get_student_id(cur, uid):
    """
    This function is to retrieve the student ID of a student based on the UID of the student's student card
    :param cur: Database Cursor
    :param uid: Unique Identifier of a student card
    :return: empty string if the student ID is not found in the database else the student ID of the student tapping on the NFC Reader
    """
    logger.info("Getting Student ID...") # logging the message on the screen for debugging purpose

    # query the database to get the student ID of the student based on the UID of the student's student card
    query = "SELECT " \
            "STUDENT_ID " \
            "FROM " \
            "STUDENT " \
            "WHERE " \
            "UID = '{}'".format(uid)

    cur.execute(query)

    result_set = cur.fetchone()

    # return empty string to the caller if the UID of the student card doesn't exist in the database else the student ID
    # belongs to the student card
    return "" if result_set is None else result_set[0]


def is_student(cur, student_id):
    """
    This function checks if a student ID exists in the database
    :param cur: Database Cursor
    :param student_id: student ID
    :return: True if the student ID exists in the database else False
    """
    logger.info("Check if {} is a valid Student ID...".format(student_id)) # logging the message on the screen for debugging purposes

    # query the STUDENT table using the student ID passed in as an argument to check if the student ID belongs to the database
    query = "SELECT " \
            "* " \
            "FROM " \
            "STUDENT " \
            "WHERE " \
            "STUDENT_ID = '{}'".format(student_id)

    cur.execute(query)

    # return True to the caller if the student ID exists in the database else False
    return False if len(cur.fetchall()) == 0 else True


def get_curr_class(cur, room_id, day, curr_time, last_class):
    """
    This function is to get the current class that is happening in the classroom passed into the function as an argument
    :param cur: Database Cursor
    :param room_id: Room ID of the classroom
    :param day: Today (ex. Monday, Tuesday, Wednesday...)
    :param curr_time: Current time to be used to look for the current class that is happenning in the classroom with room_id, {room_id}
    :param last_class: Previous class that has ended in the classroom
    :return: 0 if there is no class happening right now in the classroom else the unit code of the current class that is happening in the classroom
    """
    # query the unit code of the current class, current class start time, current class duration from the database
    query = "SELECT " \
            "UNIT_CODE, " \
            "CLASS_START_TIME, " \
            "CLASS_DURATION " \
            "FROM " \
            "ROOM_UNIT " \
            "WHERE " \
            "ROOM_ID = '{}' " \
            "AND " \
            "DAY = '{}';".format(room_id, day)

    cur.execute(query)

    classes = cur.fetchall()

    # check if there is any class on a particular day  (ex. Monday, Tuesday, Wednesday...)in the classroom
    if len(classes) > 0:

        # loop through all the classes on a particular day (ex. Monday, Tuesday, Wednesday, ...) in the classroom
        for c in classes:
            # convert the time from a Time object in python to Timedelta object to facilitate calculation
            cst = timedelta(hours=c[1].hour, minutes=c[1].minute, seconds=c[1].second)
            # check the time difference between the current time and the class start time and convert it to seconds
            dt = (cst - curr_time).total_seconds()

            # we will take the class with the class start time within +- 10 minutes from the current time and return
            # the unit code of the current class, the current class start time and the current class duration
            # we are sure that this method will always return us with the correct current class that is happening in the classroom
            # because no class will be less than an hour long and therefore the difference between the class start time
            # and the current time should be more than an hour or 3600 seconds
            if (c[0] != last_class) and (abs(dt) <= 600):
                return c

    # no class is happening right now in the classroom
    return 0


def in_right_class(cur, student_id, year, sem, curr_class):
    """
    This function checks if a student belongs to the current class that is happening right now in the classroom
    :param cur: Database Cursor
    :param student_id: student ID of the student to be check if he/she belongs to the current class that is happening right now in the classroom
    :param year: current year
    :param sem: current sem
    :param curr_class: unit code of the current class that is happening in the classroom right now
    :return: True if the student belongs to the current class else False
    """
    logger.info("Is {} in the right class?".format(student_id)) # log the message on the screen for debugging purposes

    # retrieve the unit code of all the units the student with student ID, {student ID} is currently taking
    query = "SELECT " \
            "UNIT_CODE " \
            "FROM " \
            "STUDENT_UNIT " \
            "WHERE " \
            "STUDENT_ID = '{}' " \
            "AND " \
            "YEAR = '{}' " \
            "AND " \
            "SEMESTER = '{}'".format(student_id, year, sem)

    cur.execute(query)

    # loop through all the units the student is currently taking
    for u in (cur.fetchall()):
        # if one of the units the student is taking matches with the unit code of the current class that is happening right now
        if u[0] == curr_class:
            return True

    # the student doesn't take the class that is happening right now
    return False
