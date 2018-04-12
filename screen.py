from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text
from luma.core.legacy.font import proportional, TINY_FONT, CP437_FONT

import time
import math

class Screen:
    """8x8 dotmatrix 'screen' using a max7219 chip"""

    def __init__(self):
        serial = spi(port = 0, device = 0, gpio = noop())
        # initialize a device of 3 matrices wide (24 leds) and 2 matrices high (16 leds)
        self.width = 24  # in pixels
        self.device = max7219(serial, width = self.width, height = 16, block_orientation=-90)
        # set brightness to lowest
        self.device.contrast(0)
        self.screen_sleep = False  # variable to know if screen is in sleep mode

    def display(self, top_right, bottom_right, img):
        """ Display given strings and icon on the matrix screen on corresponding locations.
            If None is given, item is not displayed """

        # if there is at least one item to display
        if top_right is not None or bottom_right is not None or img is not None:
            with canvas(self.device) as draw:
                if top_right is not None:
                    text(draw, (17, 0), top_right, fill="white", font=TINY_FONT)

                if bottom_right is not None:
                    text(draw, (17, 8), bottom_right, fill="white", font=TINY_FONT)

                if img is not None:
                    draw.bitmap((0,0), img, fill="white")
        # if there are no items to display (all 3 are None)
        else:
            self.display_text("Error")

    def display_text(self, string):
        """ displays between 1 and 12 characters on the screen in TINY_FONT
            Centers text vertically and horizontally, wrapping lines if necessary. """
        # TODO? make this really flexible with every possible width and height?
        # TODO? make it wrap at spaces if possible

        chars = len(string)
        # if string is smaller than 6 characters
        # (maximum of 6 characters fit on one line of the screen)
        if chars <= 6:
            # calculate centered x position for line
            x = self.calculate_x_pos(chars)
            with canvas(self.device) as draw:
                text(draw, (x, 4), string, fill="white", font=TINY_FONT)

        # if string is between 7 and 12 characters
        if chars > 6 and chars <= 12:
            # divide string in 2 lines
            divide = math.ceil(chars / 2)
            # calculate centered x positions for both lines
            x1 = self.calculate_x_pos(divide)
            x2 = self.calculate_x_pos(chars - divide)

            with canvas(self.device) as draw:
                text(draw, (x1, 1), string[:divide], fill="white", font=TINY_FONT)
                text(draw, (x2, 7), string[divide:], fill="white", font=TINY_FONT)

    def calculate_x_pos(self, amount_of_characters):
        """ calculate the x position so that the string can be centered horizontally
            according to the amount of character """

        # calculate amount of pixels that the string is wide
        # (one character is 3 pixels wide + 1 pixel whitespace)
        line_length = amount_of_characters * 4 - 1
        # calculate centered x position on screen
        return self.width / 2 - math.ceil(line_length / 2)

    def is_sleeping(self):
        return self.screen_sleep

    def wake_up(self):
        """ wakes the screen from a low-power sleeping state """

        self.device.show()
        self.screen_sleep = False
        print("Woke up screen")

    def go_to_sleep(self):
        """ puts the screen in a low-power sleeping state """

        self.device.hide()
        self.screen_sleep = True
        print("Put screen to sleep")
