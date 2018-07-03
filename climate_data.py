from pyowm import OWM, exceptions

import Adafruit_DHT as dht

import datetime

class ClimateData:
    """ Retrieves and logs inside and outside climate data"""

    def __init__(self, DHT22_pin, API_key):
        # Temperature & humidity sensor pin
        self.DHT22_pin = DHT22_pin
        # OpenWeatherMaps object setup
        self.owm = OWM(API_key)
        # Coordinates of the desired place to get weather info for
        # Peizegem: 50.978978, 4.211429
        # Leuven: 50.875494, 4.711183
        self.coordinates = (50.978978, 4.211429)


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
        """ returns the hour of the weatherdata, outside temperature and the weather icon.
            returns None for all values if the API can't be reached. """

        # empty values for when API can't be reached
        weather_hour = None
        outside_temp = None
        icon = None

        try:
            # Get current weather info for coordinates
            # obs = owm.weather_at_coords(50.875494, 4.711183)
            obs = self.owm.weather_at_coords(self.coordinates[0], self.coordinates[1])

            # get outside weather
            weather = obs.get_weather()
            timestamp = weather.get_reference_time()
            weather_day = datetime.datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y')
            weather_hour = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
            outside_temp = weather.get_temperature(unit = 'celsius')['temp']
            icon = weather.get_weather_icon_name()

            # print outside weather info
            self.print_outside_weather(weather, weather_day, weather_hour)

        # if the system is offline/API is not available
        except exceptions.api_call_error.APICallError:
            print("System offline")

        # return weather values
        return weather_hour, outside_temp, icon

    def get_inside_data(self):
        # get inside sensor readings
        inside_humid, inside_temp = dht.read_retry(dht.DHT22, self.DHT22_pin)  #, retries = 3, delay_seconds = 2)
        # if a reading could be gotten
        if inside_humid is not None and inside_temp is not None:
            inside_humid = round(inside_humid, 2)
            inside_temp = round(inside_temp, 2)
            # print inside data
            print("Inside temp: {}°C".format(inside_temp))
            print("Inside humidity: {}%".format(inside_humid))
        else:
            print("Couldn't get inside readings.")

        print("")

        return inside_humid, inside_temp

    def get_min_max(self):
        """ Retrieves todays minimum and maximum temperature """
        # TODO only shows min and max of first 3-hour forecast.
        # get a list of todays forecasts only and get min and max from list.
        # This list can not update everytime because the forecasts won't be from
        # the start of the day when it's 13:00

        min, max = None

        try:
            # Get 5 days of forecast info with data 3 hours apart
            forecaster = self.owm.three_hours_forecast_at_coords(self.coordinates[0], self.coordinates[1])

            # get weather object from forecaster closest to now
            # weather = forecaster.get_weather_at(datetime.datetime.now())
            weather = forecaster.get_forecast().get(0)

            # get the day and time of the retrieved weather
            timestamp = weather.get_reference_time()
            weather_day = datetime.datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y')
            weather_hour = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')

            # get the temperature info of the forecast
            temp = weather.get_temperature(unit = 'celsius')

            # print some info
            print("Min and max temperatures retrieved are from: {} {}".format(weather_day, weather_hour))
            print("Min: {}".format(temp['temp_min']))
            print("Max: {}".format(temp['temp_max']))
            print("")

            min = temp['temp_min']
            max = temp['temp_max']

        # if the system is offline/API is not available
        except exceptions.api_call_error.APICallError:
            print("System offline")

        return min, max
    # TODO def get_today_forecast_min_temp(forecaster):
