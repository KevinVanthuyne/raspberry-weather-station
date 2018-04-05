#!/usr/bin/env python3

import time
import datetime
from PIL import Image
import RPi.GPIO as GPIO

from weatherstation import WeatherStation
from database import Database
from screen import Screen
from lightsensor import LightSensor

""" Adjust these variables if needed ------------------------------------------------ """
DHT22_pin = 15  # GPIO pin on Raspberry Pi for DHT22 sensor (BCM number)
lightsensor_pin = 27  #GPIO pin connected to digital out of LM393 light sensor
API_key = '80393a1060ab07030ec77f53770a9760'  # OpenWeatherMaps API key

# Now using SQLite, if you prefer loggin to Excel, swap all Excel and Database lines
db_file = 'weatherdata.db' # name of the database file
# excel_file_name = '/home/pi/Programs/Weerstation/temperatures.xlsx'
""" --------------------------------------------------------------------------------- """

def update_screen(pin):
    print("Light change detected")
    time.sleep(0.1)

    # if it's light in the room, wake up screen
    if lightsensor.is_light():
        print("It's light!")
        if screen.is_sleeping():
            screen.wake_up()
            print("Woke up screen")
    # If the screen is not sleeping, put it in sleep mode
    else:
        print("It's dark!")
        if not screen.is_sleeping():
            screen.go_to_sleep()
            print("Put screen to sleep")


if __name__ == "__main__":
    try:
        """ Setup of all the components """
        screen = Screen()
        # Show info on screen to inform Pi is booting
        screen.display_startup()

        db = Database(db_file)
        # self.excel = Excel(excel_file_name)

        station = WeatherStation(DHT22_pin, API_key)
        lightsensor = LightSensor(lightsensor_pin)

        """ Setup interrupt for when light changes """
        GPIO.add_event_detect(lightsensor_pin, GPIO.RISING, callback=update_screen, bouncetime=200)

        """ Main loop """
        while True:
            # Get current day & time
            now = datetime.datetime.now()
            day = now.date()
            hour = now.time()
            print("It's now: {} {}".format(hour, day))

            # Get outside weather
            weather_hour, outside_temp, icon = station.get_outside_weather()

            # Get inside data
            inside_humid, inside_temp = station.get_inside_data()

            # log data to Excel
            # self.excel.write_to_excel(day, hour, weather_hour, outside_temp, inside_temp, inside_humid)

            # log data to SQLite database
            reading = (day, str(hour), str(weather_hour), outside_temp, inside_temp, inside_humid)
            db.add_reading(reading)

            # If it's light in the room, show temperature on screen
            if lightsensor.is_light():
                # get the icon image to display
                icon_path = "icons/{}.bmp".format(icon[:2])
                img = Image.open(icon_path)
                # Display current temperatures and icon
                screen.display(str(round(outside_temp)), str(round(inside_temp)), img)

            print("-----------------------------------------------------------")
            # sleep 5 minutes
            time.sleep(5 * 60)

    except KeyboardInterrupt:
        print("STOPPED")
