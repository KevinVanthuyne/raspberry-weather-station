# coding=utf-8
# !/usr/bin/env python3

# Library used:
# https://github.com/csparpa/pyowm

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text
from luma.core.legacy.font import proportional, TINY_FONT

from pyowm import OWM, exceptions

import Adafruit_DHT as dht

import sqlite3

import RPi.GPIO as GPIO

import time
import os.path
import datetime

# from excel import Excel
from database import Database



class WeatherStation:
    """ Inside and outside temperature logging"""

    def __init__(self):

        """ Adjust these variables if needed ------------------------------------------------ """
        self.DHT22_pin = 15  # GPIO pin on Raspberry Pi for DHT22 sensor (BCM number)
        self.lightsensor_pin = 27  #GPIO pin connected to digital out of LM393 light sensor
        API_key = '80393a1060ab07030ec77f53770a9760'  # OpenWeatherMaps API key

        # Now using SQLite, if you prefer loggin to Excel, swap all Excel and Database lines
        db_file = 'weatherdata.db' # name of the database file
        # excel_file_name = '/home/pi/Programs/Weerstation/temperatures.xlsx'
        """ --------------------------------------------------------------------------------- """

        # Matrix setup
        # TODO refactor to seperate class
        serial = spi(port = 0, device = 0, gpio = noop())
        self.device = max7219(serial)
        self.device.contrast(0)
        self.screen_sleep = False

        # Show X on screen to inform Pi is booting
        with canvas(self.device) as draw:
            text(draw, (0, 0), "X", fill="white", font=proportional(TINY_FONT))

        # OpenWeatherMaps object setup
        self.owm = OWM(API_key)

        # Storage setup
        # self.excel = Excel(excel_file_name)
        self.db = Database(db_file)

        # Light sensor setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.lightsensor_pin, GPIO.IN)

    def run(self):
        """ Main loop """
        while True:
            now = datetime.datetime.now()
            day = now.date()
            hour = now.time()
            print("It's now: {} {}".format(hour, day))

            try:
                # Get current weather info for Leuven
                # obs = owm.weather_at_coords(50.875494, 4.711183) # Observation
                # Peizegem city:
                obs = self.owm.weather_at_coords(50.978978, 4.211429)

                # get outside weather
                weather = obs.get_weather()
                timestamp = weather.get_reference_time()
                weather_day = datetime.datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y')
                weather_hour = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
                outside_temp = weather.get_temperature(unit = 'celsius')['temp']

                # print outside weather info
                print("Fetched data is from: {} {}".format(weather_day, weather_hour))
                print("it's now {}°C".format(outside_temp))
                print("Short weather status: {}".format(weather.get_status()))
                print("Detailed weather status: {}".format(weather.get_detailed_status()))
                print("Sunrise: {}".format(weather.get_sunrise_time('iso')))
                print("Sunset: {}".format(weather.get_sunset_time('iso')))
                print("")
            # If the system if offline/API is not available
            except exceptions.api_call_error.APICallError:
                print("System offline")
                # fill in blank values as input
                weather_day = ""
                weather_hour = ""
                outside_temp = ""

            # get inside sensor readings
            inside_humid, inside_temp = dht.read_retry(dht.DHT22, self.DHT22_pin, retries = 5, delay_seconds = 1)
            # if a reading could be gotten
            if inside_humid is not None and inside_temp is not None:
                inside_humid = round(inside_humid, 2)
                inside_temp = round(inside_temp, 2)
            else:
                inside_temp = ""
                inside_humid = ""

            # print inside data
            print("Inside temp: {}°C".format(inside_temp))
            print("Inside humidity: {}%".format(inside_humid))
            print("")

            # log data to Excel
            # self.excel.write_to_excel(day, hour, weather_hour, outside_temp, inside_temp, inside_humid)

            # log data to SQLite database
            reading = (day, str(hour), str(weather_hour), outside_temp, inside_temp, inside_humid)
            self.db.add_reading(reading)

            # If it's light in the room, show temperature
            # (Sensor output = 1 if dark, 0 if light)
            if not GPIO.input(self.lightsensor_pin):
                # If the screen is sleeping, wake it up
                if self.screen_sleep:
                    device.show()
                    self.screen_sleep = False
                    print("Woke up screen")

                # Display current temperature
                with canvas(self.device) as draw:
                    text(draw, (0, 0), str(outside_temp), fill="white", font=proportional(TINY_FONT))
            else:
                # If the screen is not sleeping, put it in sleep mode
                if not self.screen_sleep:
                    self.device.hide()  # show() switches display off
                    self.screen_sleep = True
                    print("Put screen to sleep")

            # Sleep 5 minutes
            time.sleep(5 * 60)

if __name__ == "__main__":
    try:
        station = WeatherStation()
        station.run()
    except KeyboardInterrupt:
        print("STOPPED")
