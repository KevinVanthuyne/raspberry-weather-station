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
        # direction of movement, to eliminate half steps
        self.direction = 0

    def read(self):
        """ Read the state of the rotary encoder and return -1 if the encoder moved
            counter clockwise or 1 if it moved clockwise """

        # read the current states of the input pins
        current_data_state = GPIO.input(self.data_pin)
        current_clock_state = GPIO.input(self.clock_pin)

        if current_clock_state != self.clock_state:
            # if no direction is set, set the direction first
            if self.direction == 0:
                # if both pins have a different value, the encoder is moving clockwise
                if current_data_state != current_clock_state:
                    self.direction = 1  # 1 == clockwise
                # if both pins have the same value, the encoder is moving counter clockwise
                else:
                    self.direction = -1  # -1 == counter clockwise

            # if a direction is set, reset it
            else:
                self.direction = 0

            self.clock_state = current_clock_state
            sleep(0.01)

            if self.direction != 0:
                print(self.direction)
