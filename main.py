import time

from weather_station import WeatherStation

def main():
    """ Adjust these variables if needed ------------------------------------------------
        All GPIO pin numbers are using BCM numbering """

    DHT22_pin = 15  # GPIO pin on Raspberry Pi for DHT22 sensor
    lightsensor_pin = 27  # GPIO pin connected to digital out of LM393 light sensor
    re_data = 12  # GPIO pin connected to the data pin of the rotary encoder
    re_clock = 6  # GPIO pin connected to the clock pin of the rotary encoder
    re_switch = 13  # GPIO pin connected to the switch (button) pin of the rotary encoder
    API_key = '80393a1060ab07030ec77f53770a9760'  # OpenWeatherMaps API key

    # Now using SQLite, if you prefer loggin to Excel, swap all Excel and Database lines
    db_file = 'weatherdata.db' # name of the database file
    # excel_file_name = '/home/pi/Programs/Weerstation/temperatures.xlsx'
    """ --------------------------------------------------------------------------------- """

    # create the weather station
    station = WeatherStation(DHT22_pin, lightsensor_pin, re_data, re_clock, re_switch, API_key, db_file)

    """ Main loop """
    while True:
        station.update()

        # If it's light in the room, show temperature and icon on screen
        if station.is_light():
            station.update_screen()

        station.log_to_db()

        print("-----------------------------------------------------------")
        # sleep 5 minutes
        time.sleep(5 * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("STOPPED")
