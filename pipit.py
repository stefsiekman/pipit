import time
from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO

import buttons
import rotary


def setup_lcd():
    return CharLCD("PCF8574", 0x3f)


def display_welcome(lcd):
    lcd.clear()
    lcd.cursor_pos = 0, 5
    lcd.write_string("PiPit")
    time.sleep(0.5)
    lcd.cursor_pos = 1, 4
    lcd.write_string("Welcome")
    time.sleep(0.5)
    lcd.clear()

    lcd.cursor_pos = 0, 0
    lcd.write_string("Testing LEDs...")

    buttons.flash()

    lcd.clear()


if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    buttons.setup()
    rotary.setup()

    lcd = setup_lcd()
    display_welcome(lcd)
    input("Press enter to quit\n")
    GPIO.cleanup()
