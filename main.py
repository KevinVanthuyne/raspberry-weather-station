#!/usr/bin/env python3

from weatherstation import WeatherStation

if __name__ == "__main__":
    try:
        station = WeatherStation()
        station.run()
    except KeyboardInterrupt:
        print("STOPPED")
