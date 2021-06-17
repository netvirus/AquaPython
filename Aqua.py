from AquaUtil import AquaUtil
from Database import Database

# Time parameters
lighting_enabled = True
lighting_start_hours = 9
lighting_stop_hours = 18
lighting_start_minutes = 0
oxygen_enabled = True
oxygen_start_hours = 9
oxygen_stop_hours = 22
oxygen_start_minutes = 0
feeding_enabled = True
feeding_start_hours = 9
feeding_stop_hours = 22
feeding_number_of = 2
# Flags
food = False
light = False
oxygen = False
backup_feeding = False
feeding_first_state = False
feeding_second_state = False
# Get BD connection
connect = Database()
utils = AquaUtil()


def resetAllParameters():
    global connect
    global food
    global feeding_first_hour
    global feeding_second_hour
    global feeding_first_state
    count = connect.select_from_db()
    if utils.checkTimeForFeeding(feeding_start_hours, feeding_stop_hours):
        if count == 0:
            if feeding_number_of == 1:
                feeding_first_hour = feeding_start_hours
                feeding_second_hour = feeding_stop_hours
            elif feeding_number_of == 2:
                feeding_first_hour = feeding_start_hours + 1
                feeding_second_hour = utils.getSecondHours(feeding_start_hours, feeding_stop_hours)
        elif count == 1:
            if feeding_number_of == 1:
                food = True
            elif feeding_number_of == 2:
                feeding_second_hour = utils.getSecondHours(feeding_start_hours, feeding_stop_hours)
                feeding_first_state = True
        elif count == 2:
            food = True


resetAllParameters()
while True:
    if lighting_enabled:
        lighting_timer = utils.checkTime(lighting_start_hours, lighting_stop_hours, lighting_start_minutes)
        # Disable lighting
        if light and not lighting_timer:
            print("Lighting - Disabled")
            light = False
        # Enable lighting
        elif not light and lighting_timer:
            print("Lighting - Enabled")
            light = True
    else:
        print("Lighting is disabled in config")
    if oxygen_enabled:
        oxygen_timer = utils.checkTime(oxygen_start_hours, oxygen_stop_hours, oxygen_start_minutes)
        # Disable oxygen
        if oxygen and not oxygen_timer:
            print("Oxygen - Disabled")
            oxygen = False
        # Enable oxygen
        elif not oxygen and oxygen_timer:
            print("Oxygen - Enabled")
            oxygen = True
    else:
        print("Oxygen is disabled in config")
    if feeding_enabled:
        if not food:
            if not feeding_first_state and utils.checkHour(
                    feeding_first_hour) or not feeding_second_state and utils.checkHour(feeding_second_hour):
                # ENABLE GPIO
                print("Feeding...")
                connect.save_to_db()
                count_from_database = connect.select_from_db()
                if count_from_database == feeding_number_of:
                    food = True
                elif count_from_database == 1 and feeding_number_of > 1:
                    feeding_first_state = True
        elif backup_feeding:
            print("Backup Feeding...")
            connect.save_to_db()
            backup_feeding = False
        if utils.checkHour(feeding_start_hours) and food:
            if count_from_database == 0:
                utils.resetAllParameters()
    else:
        print("Feeding is disabled in config")