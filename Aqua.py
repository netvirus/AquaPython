import time
import logging
from AquaUtil import AquaUtil
from Database import Database
import webhook_listener
import json
import RPi.GPIO as GPIO


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("aqua.log"),
        logging.StreamHandler()
    ]
)

# Web
port = 8080
# Time parameters
lighting_enabled = True
lighting_start_hours = 9
lighting_stop_hours = 18
lighting_start_minutes = 0
lighting_gpio = 17
oxygen_enabled = True
oxygen_start_hours = 9
oxygen_stop_hours = 22
oxygen_start_minutes = 0
oxygen_gpio = 27
feeding_enabled = True
feeding_start_hours = 9
feeding_stop_hours = 22
feeding_first_hour = 0
feeding_second_hour = 0
feeding_number_of = 2
feeding_gpio = 22
# Flags
debug = True
food = False
light = False
oxygen = False
backup_feeding = False
feeding_first_state = False
feeding_second_state = False
# Get BD connection
connect = Database()
utils = AquaUtil()


def parse_request(request, *args, **kwargs):
    logging.debug(
        "Received request:\n"
        + "Method: {}\n".format(request.method)
        + "Headers: {}\n".format(request.headers)
        + "Args (url path): {}\n".format(args)
        + "Keyword Args (url parameters): {}\n".format(kwargs)
        + "Body: {}".format(
            request.body.read(int(request.headers["Content-Length"]))
            if int(request.headers.get("Content-Length", 0)) > 0
            else ""
        )
    )
    return

webhooks = webhook_listener.Listener(port=port, handlers={"POST": parse_request})
webhooks.start()

def resetAllParameters():
    global connect
    global food
    global feeding_first_hour
    global feeding_second_hour
    global feeding_first_state
    count = connect.select_from_db()
    if utils.checkTimeForFeeding(feeding_start_hours, feeding_stop_hours):
        feeding_first_hour = feeding_start_hours + 1
        if count == 0:
            if feeding_number_of == 1:
                feeding_second_hour = feeding_stop_hours
            elif feeding_number_of == 2:
                feeding_second_hour = utils.getSecondHours(feeding_start_hours, feeding_stop_hours)
        elif count == 1:
            if feeding_number_of == 1:
                food = True
            elif feeding_number_of == 2:
                feeding_second_hour = utils.getSecondHours(feeding_start_hours, feeding_stop_hours)
                feeding_first_state = True
        elif count == 2:
            food = True


GPIO.setmode(GPIO.BCM)
resetAllParameters()
while True:
    if lighting_enabled:
        lighting_timer = utils.checkTime(lighting_start_hours, lighting_stop_hours, lighting_start_minutes)
        # Disable lighting
        if light and not lighting_timer:
            if debug:
                logging.info("Lighting - Disabled")
            GPIO.output(lighting_gpio, GPIO.LOW)
            GPIO.setup(lighting_gpio, GPIO.IN)
            light = False
        # Enable lighting
        elif not light and lighting_timer:
            if debug:
                logging.info("Lighting - Enabled")
            GPIO.setup(lighting_gpio, GPIO.OUT)
            GPIO.output(lighting_gpio, GPIO.HIGH)
            light = True
    else:
        logging.info("Lighting is disabled in config")
    if oxygen_enabled:
        oxygen_timer = utils.checkTime(oxygen_start_hours, oxygen_stop_hours, oxygen_start_minutes)
        # Disable oxygen
        if oxygen and not oxygen_timer:
            if debug:
                logging.info("Oxygen - Disabled")
            GPIO.output(oxygen_gpio, GPIO.LOW)
            GPIO.setup(oxygen_gpio, GPIO.IN)
            oxygen = False
        # Enable oxygen
        elif not oxygen and oxygen_timer:
            if debug:
                logging.info("Oxygen - Enabled")
            GPIO.setup(oxygen_gpio, GPIO.OUT)
            GPIO.output(oxygen_gpio, GPIO.HIGH)
            oxygen = True
    else:
        logging.info("Oxygen is disabled in config")
    if feeding_enabled:
        if not food:
            if not feeding_first_state and utils.checkHour(feeding_first_hour) or not feeding_second_state and utils.checkHour(feeding_second_hour):
                if debug:
                    logging.info("Feeding...")
                GPIO.setup(feeding_gpio, GPIO.OUT)
                GPIO.output(feeding_gpio, GPIO.HIGH)
                time.sleep(2)
                GPIO.output(feeding_gpio, GPIO.LOW)
                GPIO.setup(feeding_gpio, GPIO.IN)
                connect.save_to_db()
                count_from_database = connect.select_from_db()
                if count_from_database == feeding_number_of:
                    food = True
                    if debug:
                        logging.info("Feeding on this day is complete.")
                elif count_from_database == 1 and feeding_number_of > 1:
                    feeding_first_state = True
        elif backup_feeding:
            if debug:
                logging.info("Backup Feeding...")
            GPIO.setup(feeding_gpio, GPIO.OUT)
            GPIO.output(feeding_gpio, GPIO.HIGH)
            time.sleep(2)
            GPIO.output(feeding_gpio, GPIO.LOW)
            GPIO.setup(feeding_gpio, GPIO.IN)
            connect.save_to_db()
            backup_feeding = False
        if utils.checkHour(feeding_start_hours) and food:
            if count_from_database == 0:
                utils.resetAllParameters()
    else:
        logging.info("Feeding is disabled in config")
