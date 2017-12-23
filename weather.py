# coding=utf-8

# Library used:
# https://github.com/csparpa/pyowm

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT, TINY_FONT

from pyowm import OWM

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment

import time
import os.path
import datetime

__excel_file_name = 'temperatures.xlsx'

def run():
    # Matrix setup
    serial = spi(port = 0, device = 0, gpio = noop())
    device = max7219(serial)
    device.contrast(0)

    # Weather setup
    API_key = '80393a1060ab07030ec77f53770a9760'
    owm = OWM(API_key)

    # Excel setup
    workbook = load_workbook(__excel_file_name)

    # Main loop
    while True:
        # Sleep between 24:00 and 6:00
        now = datetime.datetime.now()
        # If it's later than 6:00
        if now.hour >= 6 and now.minute >= 0:
            print("It's now: {}".format(datetime.datetime.now().time()))
            # Get current weather info for Leuven
            # obs = owm.weather_at_coords(50.875494, 4.711183) # Observation
            # Peizegem city:
            obs = owm.weather_at_coords(50.978978, 4.211429)

            weather = obs.get_weather()
            temp = weather.get_temperature(unit = 'celsius')['temp']
            timestamp = weather.get_reference_time(timeformat = 'iso')
            # print some data
            print("Fetched data is from: {}".format(timestamp))
            print("it's now {}°C".format(temp))
            print("Short weather status: {}".format(weather.get_status()))
            print("Detailed weather status: {}".format(weather.get_detailed_status()))
            print("Sunrise: {}".format(weather.get_sunrise_time('iso')))
            print("Sunset: {}".format(weather.get_sunset_time('iso')))
            print("")

            # log data to Excel
            write_to_excel(workbook, temp, timestamp)

            # Display current temperature
            with canvas(device) as draw:
                text(draw, (0, 0), str(temp), fill="white", font=proportional(TINY_FONT))
            # Sleep 10 minutes
            time.sleep(10 * 60)
        else:
            # sleep 30 minutes
            time.sleep(30 * 60)

def create_excel():
    wb = Workbook()  # create workbook
    ws = wb.active  # select worksheet
    ws.title = "Temperature"  # set worksheet title
    # set first row (titles) to bold
    row = ws.row_dimensions[1]
    row.font = Font(bold = True)
    # fill in titles
    ws.cell(row = 1, column = 1, value = "Outside temperature")
    ws.cell(row = 1, column = 2, value = "Inside temperature")
    ws.cell(row = 1, column = 3, value = "Timestamp")
    # set column widths
    ws.column_dimensions['A'].width = 5  # Outside temperature
    ws.column_dimensions['B'].width = 5  # Inside temperature
    ws.column_dimensions['C'].width = 25  # Date

    # save the file
    wb.save(__excel_file_name)

def write_to_excel(workbook, temp, timestamp):
    sheet = workbook.active
    row = sheet.max_row + 1
    sheet.cell(row = row, column = 1, value = temp)
    sheet.cell(row = row, column = 2, value = timestamp)
    workbook.save(__excel_file_name)

    print("Written to excel. Row {}".format(row))
    print("")


if __name__ == "__main__":
    try:
        # create an excel file if there is none
        if not os.path.isfile(__excel_file_name):
            create_excel()
            print("Excel log file created")
        else:
            print("Excel log file found")

        run()
    except KeyboardInterrupt:
        print("STOPPED")
