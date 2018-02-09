from pyowm import OWM, exceptions

import Adafruit_DHT as dht

import datetime

class WeatherStation:
    """ Inside and outside temperature logging"""

    def __init__(self, DHT22_pin, API_key):
        # Temperature & humidity sensor pin
        self.DHT22_pin = DHT22_pin
        # OpenWeatherMaps object setup
        self.owm = OWM(API_key)

    def print_outside_weather(self, weather, weather_day, weather_hour):
        print("Fetched data is from: {} {}".format(weather_day, weather_hour))
        print("it's now {}°C".format(weather.get_temperature(unit = 'celsius')['temp']))
        print("Short weather status: {}".format(weather.get_status()))
        print("Detailed weather status: {}".format(weather.get_detailed_status()))
        print("Sunrise: {}".format(weather.get_sunrise_time('iso')))
        print("Sunset: {}".format(weather.get_sunset_time('iso')))
        print("Icon: {}".format(weather.get_weather_icon_name()))
        print("")

    def get_outside_weather(self):
        """ returns the hour of weatherdata, outside temperature and the weather icon """
        # blank values when system is offline
        weather_hour = ""
        outside_temp = ""
        try:
            # Get current weather info for coordinates
            # obs = owm.weather_at_coords(50.875494, 4.711183)
            obs = self.owm.weather_at_coords(50.978978, 4.211429) # Peizegem

            # get outside weather
            weather = obs.get_weather()
            timestamp = weather.get_reference_time()
            weather_day = datetime.datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y')
            weather_hour = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
            outside_temp = weather.get_temperature(unit = 'celsius')['temp']
            icon = weather.get_weather_icon_name()

            # print outside weather info
            self.print_outside_weather(weather, weather_day, weather_hour)

        # If the system if offline/API is not available
        except exceptions.api_call_error.APICallError:
            print("System offline")

        return (weather_hour, outside_temp, icon)

    def get_inside_data(self):
        # get inside sensor readings
        inside_humid, inside_temp = dht.read_retry(dht.DHT22, self.DHT22_pin, retries = 5, delay_seconds = 2)
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

        return inside_humid, inside_temp
