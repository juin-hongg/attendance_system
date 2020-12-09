from my_logging import my_logging

import datetime

#logger = my_logging.get_logger(__name__)


def get_current_week(cur, start_date, year, sem):
    """
    This function gets the current week of the current semester (ex. week 7, week 8, week 9, ...)
    :param cur: Database Cursor
    :param start_date: The start date of the current semester
    :param year: current year
    :param sem: current semester
    :return: current week of the current semester
    """
    # retrieve the last week before the semester break from the database
    query = "SELECT " \
            "WEEK_BEFORE_SEMBREAK " \
            "FROM " \
            "SEMESTER " \
            "WHERE " \
            "YEAR = '{}' " \
            "AND " \
            "SEMESTER = '{}'".format(year, sem)

    cur.execute(query)

    # convert the start date in the Datetime object to a Date object
    # start date
    strt_date = datetime.datetime.date(start_date)
    # today's date
    current_date = datetime.datetime.date(datetime.datetime.now())
    # the total number of days between the start date and today's date
    num_of_days = abs(current_date - strt_date).days
    # convert the total number of days to total number of weeks
    current_week = (num_of_days // 7) + 1
    # the last week before the semester break
    week_before_sem_break = cur.fetchone()[0]

    # check if the current week is earlier or later than the last week before the semester break
    # if the current week is later than the last week before the semester break
    # we need to deduct a week from the total number of weeks because the one week semester break is not counted
    # WE ASSUME THAT THE SEMESTER BREAK WILL ALWAYS BE A WEEK LONG
    # although in semester 2 of the year 2020, we had 2 weeks of semester break but it was  a SPECIAL CASE (due to Covid-19)
    # and the attendance for this semester is not counted
    if (week_before_sem_break < current_week):
        current_week -= 1

    return current_week


def mark_time_in(cur, student_id, unit_code, cst, year, sem, start_date):
    """
    This function marks the time in of the student taking attendance for the current class that is happening in the
    classroom right now.
    :param cur: Database Cursor
    :param student_id: the student ID of the student taking attendance for the current class
    :param unit_code: the unit code of the current class that is happening right now in the classroom
    :param cst: the current class start time, to be used to know if a student is late to the class
    :param year: the current year
    :param sem: the current sem
    :param start_date: the start date of the current semester
    :return: True if the student is late to the class else False
    """
    #logger.info("Marking attendance... (Time In)")

    curr_time = datetime.datetime.now() # current datetime
    ct = curr_time.time() # current time
    # convert the Time object to Timedelta object to facilitate calcutaion to know if a student is late to the class
    ct = datetime.timedelta(hours=ct.hour, minutes=ct.minute, seconds=ct.second)

    # True if the student is late to the class
    # a student is considered to be late to the class when the time difference between the time in and
    # class start time is more than 10 minutes/600 seconds after the class has started
    late = True if (ct > cst) and ((ct - cst).total_seconds() > 600) else False
    current_week = get_current_week(cur, start_date, year, sem)

    # insert all the data required for the dashboard showing the attendance data into the ATTENDANCE table
    query = "INSERT " \
            "INTO " \
            "ATTENDANCE " \
            "(" \
            "STUDENT_ID, " \
            "UNIT_CODE, " \
            "TIME_IN, " \
            "LATE, " \
            "WEEK, " \
            "YEAR, " \
            "SEMESTER" \
            ") " \
            "VALUES " \
            "(" \
            "'{}', '{}', '{}', '{}', '{}', '{}', '{}'" \
            ")".format(student_id, unit_code, curr_time, late, current_week, year, sem)

    cur.execute(query)

    #logger.info("Marked! (Time In)")

    # True if the student is late to the current class else False
    return late


def mark_time_out(cur, student_id, unit_code, year, sem, start_date, class_duration, elapsed_time):
    """
    This function is to mark time out when the student leaves the current class that is happening in the classroom
    :param cur: Database Cursor
    :param student_id: student ID of the student attending the current class that is happening inn the classroom
    :param unit_code: unit code of the current class that is happening in the classroom
    :param year: current year
    :param sem: current semester
    :param start_date: the start date of the current semester
    :param class_duration: the current class duration
    :param elapsed_time: how long has the tine elapsed since the class start time
    :return: True if the time out (when the student leaves the current class) of the student is marked else False
    """
    # current week of the current semester (ex. week 8, week 9, week 10, . . .)
    current_week = get_current_week(cur, start_date, year, sem)

    # retrieve the current class attendance data of the student with the student ID, {student_id} in the ATTENDANCE table
    query = "SELECT " \
            "* " \
            "FROM " \
            "ATTENDANCE " \
            "WHERE " \
            "STUDENT_ID = '{}' " \
            "AND " \
            "UNIT_CODE = '{}' " \
            "AND " \
            "WEEK = '{}' " \
            "AND " \
            "YEAR = '{}' " \
            "AND " \
            "SEMESTER = '{}'".format(student_id, unit_code, current_week, year, sem)

    cur.execute(query)

    result_set = cur.fetchone()

    # mark time out of the student only when these conditions are FULFILLED
    # 1. the result set is not None, that means the current class attendance data of the student with the student ID, {student_id} exists in the database
    # 2. students can start marking time out starting from 10 minutes/600 seconds before the current class ends
    # 3. the time out (when the student leaves the class) of the student still hasn't been marked
    if (result_set is not None) and (result_set[4] is None) and (elapsed_time >= class_duration - 600):

        # current time
        curr_time = datetime.datetime.now()
        # update the current class attendance data of the student with the student ID, {student_id} to include time out
        query = "UPDATE " \
                "ATTENDANCE " \
                "SET " \
                "TIME_OUT = '{}' " \
                "WHERE " \
                "STUDENT_ID = '{}' " \
                "AND " \
                "UNIT_CODE = '{}' " \
                "AND " \
                "WEEK = '{}' " \
                "AND " \
                "YEAR = '{}' " \
                "AND " \
                "SEMESTER = '{}'".format(curr_time, student_id, unit_code, current_week, year, sem)

        cur.execute(query)

        #logger.info("Attendance is marked! (Time Out)")
        # the time out of the student (when the student leaves the current class) is marked
        return True

    # time out of the student (when the student leaves the current class) is not marked
    return False
