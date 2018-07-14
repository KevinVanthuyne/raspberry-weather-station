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
        """ Retrieves todays weather forecasts with minimum and maximum temperature.
            Doesn't keep min and max from earlier in the day"""

        min = None
        max = None

        try:
            # Get 5 days of forecast info with data 3 hours apart
            forecaster = self.owm.three_hours_forecast_at_coords(self.coordinates[0], self.coordinates[1])

            forecast = forecaster.get_forecast()
            weathers = forecast.get_weathers()

            # get forecasts of today
            today = datetime.datetime.now() #+ datetime.timedelta(days=1)
            todays_weathers = self.get_forecasts_of_day(weathers, today)

            # select hottest and coldest weathers
            hottest = self.hottest_weather(todays_weathers)
            max = hottest.get_temperature(unit='celsius')['temp_max']

            coldest = self.coldest_weather(todays_weathers)
            min = coldest.get_temperature(unit='celsius')['temp_min']

            # print some info
            print("Min: {} (at {})".format(min, coldest.get_reference_time(timeformat='iso')))
            print("Max: {} (at {})".format(max, hottest.get_reference_time(timeformat='iso')))
            print("")

        # if the system is offline/API is not available
        except exceptions.api_call_error.APICallError:
            print("System offline")

        return coldest, hottest

    def get_forecasts_of_day(self, weathers, date):
        """ takes a list of weather objects contained by a forecast object and
            returns only the weathers for the day given by the datetime object """

        # list of weathers to return
        selection = []

        for weather in weathers:
            # get the reference time of the weather object as a datetime object
            ref_time = weather.get_reference_time(timeformat='date')

            # if the weather's day equals the given date
            if date.day == ref_time.day and date.month == ref_time.month and date.year == ref_time.year:
                selection.append(weather)
                print("Selected: {}".format(ref_time))

        return selection

    def hottest_weather(self, weathers):
        """ returns the weather with the highest max temperature, given a list of weathers """

        # if weathers is not empty, process list
        if weathers:
            max = weathers[0]

            for weather in weathers:
                if weather.get_temperature(unit='celsius')['temp_max'] > max.get_temperature(unit='celsius')['temp_max']:
                    max = weather

            return max
        else:
            return None

    def coldest_weather(self, weathers):
        """ returns the weather with the lowest min temperature, given a list of weathers """

        if weathers:
            min = weathers[0]

            for weather in weathers:
                if weather.get_temperature(unit='celsius')['temp_min'] < min.get_temperature(unit='celsius')['temp_min']:
                    min = weather

            return min
        else:
            return None
