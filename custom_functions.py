import pyowm

from datetime import datetime, timedelta


def get_elapsed_time(cst):
    """
    This function gets the time elapsed since the current class start time
    :param cst: current class start time
    :return: 0 if the  current time is EARLIER than the current class start time else the total time elapsed in seconds
    """
    # current time
    curr_time = datetime.now().time()
    # current time converted from Time object to Timedelta object to facilitate calculation
    curr_time = timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=curr_time.second)

    # 0 if the current time is EARLIER than the current class start time else the total time elapsed
    return (curr_time - cst).total_seconds() if (curr_time > cst) else 0


def set_current_weather(cur, unit_code, year, sem, week, cst):
    """
    This function is to retrieve current weather status of KUALA LUMPUR, SELANGOR through web API and
    save the data into the database
    :param cur: Database Cursor
    :param unit_code: the unit code of the current class
    :param year: current year
    :param sem: current semester
    :param week: current week of the current semester
    :param cst: current class start time
    :return: None
    """
    # retrieve the current weather status of KUALA LUMPUR, SELANGOR through web API
    owm = pyowm.OWM("38a7ee6448c1e85e81a48536316502db")
    weather = (owm.weather_at_place("Kuala Lumpur, Malaysia")).get_weather()
    status = weather.get_status()

    # insert the weather status when the current class is happening in the classroom into the database
    # to facilitate data analytics on the web dashboard
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

    cur.execute(query)


def get_start_date(cur, year, sem):
    """
    This function is to get the start date of the current semester
    :param cur: Database Cursor
    :param year: current year
    :param sem: current semester
    :return: the start date of the current semester
    """
    # retrieve the start date of the current semester
    query = "SELECT " \
            "START_DATE " \
            "FROM " \
            "SEMESTER " \
            "WHERE " \
            "YEAR = '{}' " \
            "AND " \
            "SEMESTER = '{}'".format(year, sem)

    cur.execute(query)

    # convert the start date from a string to a Datime object to facilitate the calculation process
    start_date = datetime.strptime(cur.fetchall()[0][0], '%Y-%m-%d')

    # start date in Datetime type
    return start_date
