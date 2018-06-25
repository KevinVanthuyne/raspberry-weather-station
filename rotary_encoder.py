import RPi.GPIO as GPIO
import threading
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

        self.lock = threading.Lock()

    def read(self, channel):
        """ Interrupt callback function called by both rotary encoder pins
            to read the state of the rotary encoder and return -1 if
            the encoder moved counter clockwise or 1 if it moved clockwise.

            Parameters: channel = GPIO pin of interrupt """

        # read the current states of the input pins
        current_data_state = GPIO.input(self.data_pin)
        current_clock_state = GPIO.input(self.clock_pin)

        # ignore interrupt if the current states haven't changed from the previous ones
        if current_data_state != self.data_state and current_clock_state != self.clock_state:
            # update states with current states
            self.data_state = current_data_state
            self.clock_state = current_clock_state

            # if both states are active
            if (current_data_state and current_clock_state):
                self.lock.acquire()
                direction = 0
                # if the channel that called the interrupt is the data pin,
                # the encoder moved clockwise
                if (channel == self.data_pin):
                    direction = 1
                # if the channel that called the interrupt is the clock pin,
                # the encoder moved counter clockwise
                elif (channel == self.clock_pin):
                    direction = -1
                self.lock.release()

                return direction
        else:
            print("Not changed")
