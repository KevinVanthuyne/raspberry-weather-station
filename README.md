# Raspberry Weatherstation
A simple weatherstation using a Raspberry, a temperature sensor and the OpenWeatherMaps API.
Uses SQLite to log all the data.

## Setup

Install the necessary packages.
- [luma.led_matrix](https://github.com/rm-hull/luma.led_matrix)
- [pyowm](https://github.com/csparpa/pyowm)
- [Adafruit_Python_DHT](https://github.com/adafruit/Adafruit_Python_DHT)
- SQLite3 or Openpyxl if needed

Add the weatherstation script to run on boot with a cronjob: `crontab -e`
Add the following contents to the file. This outputs all console output to a log file.
```
@reboot python3 -u <path-to-script>/main.py > <path-to-script>/weatherstation.log 2>&1 &
```

Optional: give the Raspberry a static ip address for easy access. Open the dhcp config file with `sudo nano /etc/dhcpcd.conf`.
Add the following contents to the file, replacing x and y values according to your situation:
```
interface eth0

static ip_address=192.168.x.y/24
static routers=192.168.x.1
static domain_name_servers=192.168.x.1

interface wlan0

static ip_address=192.168.x.y/24
static routers=192.168.x.1
static domain_name_servers=192.168.x.1

```
