from abc import ABC, abstractmethod
from PIL import Image

class Page(ABC):
    """ abstract Page class containing a WeatherStation to display
        the right information of that page"""

    @abstractmethod
    def __init__(self, weather_station):
        self.weather_station = weather_station

    @abstractmethod
    def update(self):
        """ update the information shown on the page """
        pass

class CurrentWeatherPage(Page):
    """ Page showing the current inside and outside temperatures,
        as well as the current weather icon """

    def __init__(self, weather_station):
        super().__init__(weather_station)

    def update(self):
        outside_temp = None
        inside_temp = None
        img = None

        # if outside weather is available
        if self.weather_station.weather_hour is not None:
            outside_temp = str(round(self.weather_station.outside_temp))
            # get the icon image to display
            icon_path = "icons/{}.bmp".format(self.weather_station.icon[:2])
            img = Image.open(icon_path)

        #if inside weather is available
        if self.weather_station.inside_temp is not None:
            inside_temp = str(round(self.weather_station.inside_temp))

        self.weather_station.screen.display(outside_temp, inside_temp, img)
        print("Screen updated.")

class MinMaxTemperaturePage(Page):
    """ Page showing the minimum and maximum temperatur of today """

    def __init__(self, weather_station):
        super().__init__(weather_station)

    def update(self):
        self.weather_station.screen.display_text("MinMax")
