#!/usr/bin/env python3

import time
import datetime
from PIL import Image
import RPi.GPIO as GPIO

from climate_data import ClimateData
from database import Database
from screen import Screen
from lightsensor import LightSensor

class WeatherStation:
    """ Facade class for all functionality of the weather station """

    def __init__(self, DHT22_pin, lightsensor_pin, API_key, db_file):
        """ Setup of all the components """
        self.screen = Screen()
        # Show info on screen to inform Pi is booting
        self.screen.display_startup()

        self.db = Database(db_file)
        # self.excel = Excel(excel_file_name)

        self.climate = ClimateData(DHT22_pin, API_key)
        self.lightsensor = LightSensor(lightsensor_pin)

        """ Setup interrupt for when light changes """
        GPIO.add_event_detect(lightsensor_pin, GPIO.RISING, callback=self.light_change, bouncetime=200)

    def update(self):
        """ Update all weather station data """
        # update outside weather
        self.weather_hour, self.outside_temp, self.icon = self.climate.get_outside_weather()

        # update inside data
        self.inside_humid, self.inside_temp = self.climate.get_inside_data()

        # update day & time of WeatherStation data with current day & time
        now = datetime.datetime.now()
        self.day = now.date()
        self.hour = now.time()

        print("Weather station updated at: {} {}".format(self.hour, self.day))


    def light_change(self, pin):
        """ interrupt handler for when a light change has been detected"""
        time.sleep(0.1)

        # if it's light in the room, wake up screen
        if self.lightsensor.is_light():
            if self.screen.is_sleeping():
                self.screen.wake_up()
                print("Woke up screen")
            # update screen with latest info
            self.update_screen()

        # If the screen is not sleeping, put it in sleep mode
        else:
            if not self.screen.is_sleeping():
                self.screen.go_to_sleep()
                print("Put screen to sleep")

    def update_screen(self):
        """ update information on the screen with current weather station data
            WeatherStation should be updated first with update() """
        # get the icon image to display
        icon_path = "icons/{}.bmp".format(self.icon[:2])
        img = Image.open(icon_path)
        # Display current temperatures and icon
        self.screen.display(str(round(self.outside_temp)), str(round(self.inside_temp)), img)

        print("Screen updated.")

    def log_to_db(self):
        """ Log the current weather station data to the database
            WeatherStation should be updated first with update() """
        # log data to Excel
        # self.excel.write_to_excel(self.day, self.hour, self.weather_hour, self.outside_temp, self.inside_temp, self.inside_humid)

        # log data to SQLite database
        reading = (self.day, str(self.hour), str(self.weather_hour), self.outside_temp, self.inside_temp, self.inside_humid)
        self.db.add_reading(reading)

    def is_light(self):
        return self.lightsensor.is_light()
