from abc import ABC, abstractmethod
from PIL import Image
from pathlib import Path

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

    @abstractmethod
    def click(self):
        """ handler method when a page is clicked """
        pass

class CurrentWeatherPage(Page):
    """ Page showing the current inside and outside temperatures,
        as well as the current weather icon """

    def __init__(self, weather_station, base_path):
        super().__init__(weather_station)
        self.base_path = base_path

    def update(self):
        outside_temp = None
        inside_temp = None
        img = None

        # if outside weather is available
        if self.weather_station.weather_hour is not None:
            outside_temp = str(round(self.weather_station.outside_temp))
            # get the icon image to display
            icon_file = Path(self.base_path) / "icons/{}.bmp".format(self.weather_station.icon[:2])
            img = Image.open(icon_file)

        #if inside weather is available
        if self.weather_station.inside_temp is not None:
            inside_temp = str(round(self.weather_station.inside_temp))

        self.weather_station.screen.display(outside_temp, inside_temp, img)
        print("Screen updated.")

    def click(self):
        print("CurrentWeatherPage clicked")

class MinMaxTemperaturePage(Page):
    """ Page showing the minimum and maximum temperature of today """

    def __init__(self, weather_station):
        super().__init__(weather_station)

    def update(self):
        outside_temp = None
        inside_temp = None
        img = None

        # if a forecast is available
        if self.weather_station.today_min is not None:
            min = "Min:{}".format(str(round(self.weather_station.today_min)))
            max = "Max:{}".format(str(round(self.weather_station.today_max)))

        self.weather_station.screen.display_top_bottom(min, max)
        print("Screen updated.")

    def click(self):
        print("Min max clicked")

class SettingsPage(Page):
    """ A page containing different settings and shutdown option """

    def __init__(self, weather_station, base_path):
        super().__init__(weather_station)
        self.base_path = base_path

    def update(self):
        # get the cogwheel image to display
        icon_file = Path(self.base_path) / "icons/cog.bmp"
        img = Image.open(icon_file)
        self.weather_station.screen.display_bitmap(img)

    def click(self):
        print("SettingsPage clicked")
