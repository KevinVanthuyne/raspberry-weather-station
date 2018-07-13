#!/usr/bin/env python3

import time
import datetime
from PIL import Image
import RPi.GPIO as GPIO

from climate_data import ClimateData
from database import Database
from screen import Screen
from lightsensor import LightSensor
from rotary_encoder import RotaryEncoder
import pages as PAGES

class WeatherStation:
    """ Facade class for all functionality of the weather station """

    def __init__(self, DHT22_pin, lightsensor_pin, re_data, re_clock, re_switch, API_key, db_file, base_path):
        """ Setup of all the components """

        self.screen = Screen()
        # Show info on screen to inform Pi is booting
        self.screen.display_text("BOOTING")

        self.db = Database(db_file, base_path)
        # self.excel = Excel(excel_file_name)

        self.climate = ClimateData(DHT22_pin, API_key)

        self.lightsensor = LightSensor(lightsensor_pin)
        # Setup interrupt for when light changes
        GPIO.add_event_detect(lightsensor_pin, GPIO.RISING, callback=self.light_changed, bouncetime=200)

        self.rotary = RotaryEncoder(re_data, re_clock, re_switch)
        # setup interrupts for rotary encoder is turned
        GPIO.add_event_detect(re_data, GPIO.RISING, callback=self.rotary_encoder_changed)
        GPIO.add_event_detect(re_clock, GPIO.RISING, callback=self.rotary_encoder_changed)
        GPIO.add_event_detect(re_switch, GPIO.FALLING, callback=self.rotary_encoder_clicked, bouncetime=200)

        # setup different pages
        self.pages = []
        self.pages.append(PAGES.CurrentWeatherPage(self, base_path))
        self.pages.append(PAGES.MinMaxTemperaturePage(self))
        self.pages.append(PAGES.SettingsPage(self, base_path))

        # index of the current page
        self.current_page = 0


    def update(self):
        """ Update all weather station data """

        # update outside weather
        self.weather_hour, self.outside_temp, self.icon = self.climate.get_outside_weather()

        # update inside data
        self.inside_humid, self.inside_temp = self.climate.get_inside_data()

        # update today's forecast data
        self.coldest, self.hottest = self.climate.get_min_max()

        # update day & time of WeatherStation data with current day & time
        now = datetime.datetime.now()
        self.day = now.date()
        self.hour = now.time()

        # TODO update all pages with current weatherstation?

        print("Weather station updated at: {} {}".format(self.hour, self.day))


    def light_changed(self, pin):
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
        """ update information on the screen with current weather station data.
            WeatherStation should be updated first with update() """

        self.pages[self.current_page].update()

    def rotary_encoder_changed(self, channel):
        result = self.rotary.read(channel)

        # current page object
        page = self.pages[self.current_page]

        # show next page
        if result == 1:
            # if the current page is not browsing its sub pages, go to next main page
            if page.current_page == None:
                # if the index is at the last page, loop back to first page
                if self.current_page == len(self.pages) - 1:
                    self.current_page = 0
                else:
                    self.current_page += 1
                print("Main page up")

            # if the current page is browsing its sub pages, go to next subpage
            else:
                # if the index is at the last page, loop back to first page
                if page.current_page == len(page.pages) - 1:
                    page.current_page = 0
                else:
                    page.current_page += 1
                print("Sub page up")

        # show previous page
        elif result == -1:
            # if the current page is not browsing its sub pages, go to previous main page
            if page.current_page == None:
                # if the index is at the first page, loop back to last page
                if self.current_page == 0:
                    self.current_page = len(self.pages) - 1
                else:
                    self.current_page -= 1
                print("Main page down")

            # if the current page is browsing its sub pages, go to previous subpage
            else:
                # if the index is at the last page, loop back to last page
                if page.current_page == 0:
                    page.current_page = len(page.pages) - 1
                else:
                    page.current_page -= 1
                print("Sub page down")

        self.update_screen()

    def rotary_encoder_clicked(self, channel):
        """ directs the click to a handler method of the current page and updates screen """
        self.pages[self.current_page].click()
        self.pages[self.current_page].update()

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
