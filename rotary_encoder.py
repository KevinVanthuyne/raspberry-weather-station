import RPi.GPIO as GPIO
from time import sleep

class RotaryEncoder:
    """ Handling class for a rotary encoder """

    def __init__(self, data_pin, clock_pin, switch_pin):
        self.data_pin = data_pin  # DT pin (Out A)
        self.clock_pin = clock_pin  # CLK pin (Out B)
        self.switch_pin = switch_pin  # SW pin

        # setup GPIO pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(data_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        GPIO.setup(clock_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        GPIO.setup(switch_pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

        # initialize Data & Clock states
        self.data_state = GPIO.input(self.data_pin)
        self.clock_state = GPIO.input(self.clock_pin)

        self.counter = 0

    def read(self):
        # read the current states of the input pins
        current_data_state = GPIO.input(self.data_pin)
        current_clock_state = GPIO.input(self.clock_pin)

        if current_clock_state != self.clock_state:
            if current_data_state != current_clock_state:
                self.counter += 1
            else:
                self.counter -= 1

            print(self.counter)
            self.clock_state = current_clock_state
            sleep(0.01)
