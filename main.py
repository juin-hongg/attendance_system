import sys
sys.path.append("../../../")
import time
import RPi.GPIO as GPIO
import pyowm
import subprocess

from cfg.config import read_yaml_file
from custom_functions import get_elapsed_time, set_current_weather, get_start_date
from datetime import datetime, timedelta
from db.DatabaseCursor import DatabaseCursor
from verif.verifier import get_student_id, is_student, get_curr_class, in_right_class
from update_attendance.update_attendance import get_current_week, mark_time_in, mark_time_out


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

CFG = read_yaml_file("cfg/config.yaml") # Configuration YAML file
YEAR = CFG.get("YEAR") # current year
SEM = CFG.get("SEM") # current semester
ROOM_ID = CFG.get("ROOM_ID") # the room ID of the classroom where this application will be running on
CONN_STR = CFG.get("DB") # connection string to connect to the database
TODAY = datetime.today().strftime("%A") # today (ex. monday, tuesday, wednesday, ...)

# indicator light
# 1. when the student enters the current class ON TIME
# 2. when the student leaves the current class
# 3. the attendance of the student has already been marked
GREEN = 21
# the student is late to the current class
YELLOW = 12
# 1. the student doesn't belong to Monash University
# 2. the student doesn't belong to the current class
RED = 16


def get_led_light(code):
    """
    This function is to turn on the appropriate indicator light according to the code passed in as argument
    :param code: this code is to determine which indicator light to be lighten up
    :return: A LED light is lighten up, ex. GREEN, RED or YELLOW LED light is lighten up
    """
    GPIO.setup(code, GPIO.OUT)
    GPIO.output(code, GPIO.HIGH)

    time.sleep(1) # the indicator light will light up for 2 seconds

    GPIO.output(code, GPIO.LOW)


if __name__ == "__main__":

    # retrieve the database cursor using the connection string
    # context manager to achieve efficient resource management without having to manually exit the database connection
    with DatabaseCursor(CONN_STR) as cur:

        unit_code = None # initially no class is happening in the classroom for today

        while True:

            curr_datetime = datetime.now() # current datetime
            curr_time = curr_datetime.time() # current time
            # convert current time from a Datetime object to Timdelta object
            curr_time = timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=curr_time.second)

            curr_class = get_curr_class(cur, ROOM_ID, TODAY, curr_time, unit_code) # get the current class that is happening in the classroom
            if curr_class != 0: # there is a class that is happening right now in the classroom

                unit_code = curr_class[0] # unit code of the current class
                cst = curr_class[1] # current class start time
                # convert the current class start time to Timdelta object to facilitate calculation
                cst = timedelta(hours=cst.hour, minutes=cst.minute, seconds=cst.second)
                duration = curr_class[2] # current class duration

                # current weeek in the current semester
                current_week = get_current_week(cur, get_start_date(cur, YEAR, SEM), YEAR, SEM)
                # insert the weather status for the current class into the database
                set_current_weather(cur, unit_code, YEAR, SEM, current_week, curr_datetime)

                has_ended = False # flag to check if the current class is over
                while not has_ended: # keep iterating if the current class is still not ended yet

                    print("\nYou may now tap your Student Card on the NFC Reader...")
                    print("\nPlease place it for 2 secs before removing...")

                    no_error = False # check for the wiring of NFC Reader to make sure the connection is good
                    while not no_error:

                        try:

                            lines = subprocess.check_output("/usr/bin/nfc-poll", stderr=open("/dev/null", "w"))

                            for l in lines.splitlines():
                                l = l.split()

                                if (l[0].decode("utf-8") == "UID"):
                                    uid_list = l
                                    break

                            no_error = True

                        except Exception as e:
                            pass

                    uid = uid_list[2]  # UID of the student card
                    for i in range(3, len(uid_list)):
                        uid += uid_list[i]

                    uid = uid.decode("utf-8")

                    student_id = get_student_id(cur, uid) # retrieve the student ID that is tie to the UID of the student card

                    # check if the student ID is valid
                    if (is_student(cur, student_id)):

                        has_ended = get_elapsed_time(cst) > duration # check if the current class is OVER

                        if has_ended:
                            print("{}, {} has ended!".format(student_id, unit_code))
                            break

                        # check if the student belongs to the current class
                        elif (in_right_class(cur, student_id, YEAR, SEM, unit_code)):

                            try:
                                # mark time out (when the student leaves the class) of the student
                                if mark_time_out(cur, student_id, unit_code, YEAR, SEM, get_start_date(cur, YEAR, SEM), duration, get_elapsed_time(cst)):
                                    print("Attendance taken! (Time Out)")
                                    get_led_light(GREEN) # GREEN light will light up

                                else:
                                    # mark time in (when the student enters the class) of the student
                                    is_late = mark_time_in(cur, student_id, unit_code, cst, YEAR, SEM, get_start_date(cur, YEAR, SEM))
                                    print("Attendance taken! (Time In)")
                                    # YELLOW light will light up if the student is late to the class else GREEN
                                    get_led_light(YELLOW) if is_late else get_led_light(GREEN)

                            except Exception as e:
                                print("Attendance has already been taken!")
                                # GREEN light if the attendance of the student has already been taken (time in / time out)
                                get_led_light(GREEN)

                        else:
                            print("{} doesn't belong to the class, {}!".format(student_id, unit_code))

                            get_led_light(RED) # student doesn't belong to the current class

                    else:
                        print("Invalid Student ID!".format(student_id))

                        get_led_light(RED) # student doesn't belong to Monash University
