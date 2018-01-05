import RPi.GPIO as GPIO

class LightSensor:
    """ Handling class for the LM393 light sensor """

    def __init__(self, lightsensor_pin):
        self.lightsensor_pin = lightsensor_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(lightsensor_pin, GPIO.IN)

    def is_light(self):
        """ Returns True if the lightsensor detects light, otherwise False """
        # (Sensor output = 1 if dark, 0 if light)
        if not GPIO.input(self.lightsensor_pin):
            return True
        return False
