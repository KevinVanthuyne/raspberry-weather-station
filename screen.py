from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text
from luma.core.legacy.font import proportional, TINY_FONT, CP437_FONT

class Screen:
    """8x8 dotmatrix 'screen' using a max7219 chip"""

    def __init__(self):
        serial = spi(port = 0, device = 0, gpio = noop())
        # initialize a device of 3 matrices wide (24 leds) and 2 matrices high (16 leds)
        self.device = max7219(serial, width = 24, height = 16, block_orientation=-90)
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
            print("No info to display on screen...")

    def display_startup(self):
        # TODO refactor to one standard text display
        # wraps text on multiple lines if too big
        """ Show info on screen to inform Pi is booting """

        with canvas(self.device) as draw:
            text(draw, (4, 1), "BOOT", fill="white", font=TINY_FONT)
            text(draw, (6, 7), "ING..", fill="white", font=TINY_FONT)

    def display_args(self, *args):
        # if one string argument is given
        if len(args) == 1 and isinstance(args[0], str):
            # display in bottom right
            with canvas(self.device) as draw:
                text(draw, (17, 8), args[0], fill="white", font=TINY_FONT)
        # if one string and one bitmap argument are given
        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], bitmap):
            # display bitmap and top right
            with canvas(self.device) as draw:
                text(draw, (17, 0), top_right, fill="white", font=TINY_FONT)
                draw.bitmap((0,0), img, fill="white")
        # if two strings and one bitmap is given
        elif len(args) == 3 and isinstance(args[0], str) and isinstance(args[1], str) and isinstance(args[2], bitmap):
            # display everything
            with canvas(self.device) as draw:
                text(draw, (17, 0), top_right, fill="white", font=TINY_FONT)
                text(draw, (17, 8), bottom_right, fill="white", font=TINY_FONT)
                draw.bitmap((0,0), img, fill="white")

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
