import time
import logging
from AquaUtil import AquaUtil
from Database import Database
#import RPi.GPIO as GPIO

from Feeding import Feeding

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("aqua.log"),
        logging.StreamHandler()
    ]
)


# Time parameters
_reset_time = 00
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
_feeding_start_hours = 12
_feeding_stop_hours = 22
_feeding_second_hour = 0
_feeding_number_of = 2
feeding_gpio = 22
# Flags
debug = True
gpio_support = False
food = False
light = False
oxygen = False
feeding_first_state = False
# Get BD connection
connect = Database()
utils = AquaUtil()


def reset_all_parameters():
    global connect
    global food
    global _feeding_start_hours
    global _feeding_stop_hours
    global _feeding_second_hour
    global feeding_first_state
    global _feeding_number_of
    if debug:
        print("Configuring all parameters...")
    count = connect.select_from_db()
    # Если не кормили еще не разу
    if count == 0:
        # Если должны кормить всего 1 раз
        if _feeding_number_of == 2:
            _feeding_second_hour = utils.getSecondHours(_feeding_start_hours, _feeding_stop_hours)
    elif count == 1:
        if _feeding_number_of == 1:
            # Откормили на сегодня
            food = True
        elif _feeding_number_of == 2:
            _feeding_second_hour = utils.getSecondHours(_feeding_start_hours, _feeding_stop_hours)
            # Покормили только один раз и надо еще один
            feeding_first_state = True
    elif count == 2:
        # Откормили на сегодня
        food = True
    # End of reset_all_parameters()

def start_feeding():
    if gpio_support:
        GPIO.setup(feeding_gpio, GPIO.OUT)
        GPIO.output(feeding_gpio, GPIO.HIGH)
        time.sleep(5)
        GPIO.output(feeding_gpio, GPIO.LOW)
        GPIO.setup(feeding_gpio, GPIO.IN)
    connect.save_to_db()
    if debug:
        print("Feeding...")
    # End of start_feeding()


if gpio_support:
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)

logging.info("= Starting Aqua Control Center =")
reset_all_parameters()


while True:
    if lighting_enabled:
        lighting_timer = utils.checkTime(lighting_start_hours, lighting_stop_hours, lighting_start_minutes)
        # Disable lighting
        if light and not lighting_timer:
            if debug:
                logging.info("Lighting - Disabled")
            if gpio_support:
                GPIO.output(lighting_gpio, GPIO.LOW)
                GPIO.setup(lighting_gpio, GPIO.IN)
            light = False
        # Enable lighting
        elif not light and lighting_timer:
            if debug:
                logging.info("Lighting - Enabled")
            if gpio_support:
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
            if gpio_support:
                GPIO.output(oxygen_gpio, GPIO.LOW)
                GPIO.setup(oxygen_gpio, GPIO.IN)
            oxygen = False
        # Enable oxygen
        elif not oxygen and oxygen_timer:
            if debug:
                logging.info("Oxygen - Enabled")
            if gpio_support:
                GPIO.setup(oxygen_gpio, GPIO.OUT)
                GPIO.output(oxygen_gpio, GPIO.HIGH)
            oxygen = True
    else:
        logging.info("Oxygen is disabled in config")
    if feeding_enabled:
        if not food:
            if utils.checkTimeForFeeding(_feeding_start_hours, _feeding_stop_hours):
                if utils.checkHour(_feeding_start_hours) and not feeding_first_state:
                    start_feeding()
                    # Выставляем флаг откормлено 1 раз
                    feeding_first_state = True
                elif utils.checkHour(_feeding_second_hour):
                    start_feeding()
                    # Выставляем флаг откормлено на сегодня
                    feed = True
        else:
            if utils.checkHour(_reset_time):
                reset_all_parameters()
    else:
        logging.info("Feeding is disabled in config")