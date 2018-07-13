from abc import ABC, abstractmethod
from PIL import Image
from pathlib import Path

class Page(ABC):
    """ abstract Page class containing a WeatherStation to display
        the right information of that page"""

    @abstractmethod
    def __init__(self, weather_station):
        self.weather_station = weather_station
        self.pages = []  # list of subpages
        self.current_page = None  # index of the current subpage (None = main page, 1 = first sub page)

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

""" ---------------------------------------------------------
        Settings
    --------------------------------------------------------- """

class SettingsPage(Page):
    """ A page containing different settings and shutdown option """

    def __init__(self, weather_station, base_path):
        super().__init__(weather_station)
        self.base_path = base_path

        # setup subpages
        self.pages.append(ShutdownPage(weather_station))
        self.pages.append(BackPage(weather_station))

    def update(self):
        # if currently on the main settings page, show cogwheel
        if self.current_page == None:
            # get the cogwheel image to display
            icon_file = Path(self.base_path) / "icons/cog.bmp"
            img = Image.open(icon_file)
            self.weather_station.screen.display_bitmap(img)
        # if on a subpage, redirect update to the subpage
        else:
            self.pages[self.current_page].update()

    def click(self):
        # if clicked on settings page, go to the first subpage
        if self.current_page == None:
            self.current_page = 0
        # if clicked when not on settings page, redirect click to subpage
        else:
            subpage = self.pages[self.current_page]
            # redirect click to subpage
            subpage.click()

            # if clicked on the BackPage, go back to the main page
            if type(subpage) is BackPage:
                self.current_page = None

class ShutdownPage(Page):
    """ A page under the SettingsPage showing 'shutdown?'
        that shuts down the Raspberry when clicked """

    def __init__(self, weather_station):
        super().__init__(weather_station)

    def update(self):
        self.weather_station.screen.display_text("Shutdown?")

    def click(self):
        print("Shutdown clicked")

class BackPage(Page):
    """ A page showing 'back?' that returns to the main page when clicked """

    def __init__(self, weather_station):
        super().__init__(weather_station)

    def update(self):
        self.weather_station.screen.display_text("BACK?")

    def click(self):
        print("Back clicked")
