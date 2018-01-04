from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text
from luma.core.legacy.font import proportional, TINY_FONT, CP437_FONT

class Screen:
    """8x8 dotmatrix 'screen' using a max7219 chip"""

    def __init__(self):
        serial = spi(port = 0, device = 0, gpio = noop())
        self.device = max7219(serial)
        self.device.contrast(0)
        self.screen_sleep = False  # variable to know if screen is in sleep mode

    def display(self, string):
        """ Display a string on the matrix screen """
        with canvas(self.device) as draw:
            text(draw, (0, 0), string, fill="white", font=proportional(TINY_FONT))

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
