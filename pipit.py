import time
from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO

import buttons
import rotary
import beacon


lcd =  CharLCD("PCF8574", 0x3f)


def display_welcome():
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


def connect_xplane():
    lcd.clear()
    lcd.cursor_pos = 0, 0
    lcd.write_string("Trying to find\n\rX-Plane...")

    beacon_info = beacon.listen(5)

    lcd.clear()
    lcd.cursor_pos = 0, 3
    lcd.write_string("Connection")

    if beacon_info is None:
        lcd.cursor_pos = 1, 5
        lcd.write_string("Failed")
        GPIO.cleanup()
        exit(1)
    else:
        lcd.cursor_pos = 1, 7
        lcd.write_string("OK")

    time.sleep(0.75)
    lcd.clear()
    lcd.cursor_pos = 0, 4
    lcd.write_string("Hostname")
    lcd.cursor_pos = 1, 0
    lcd.write_string(beacon_info[2])
    
    time.sleep(2)


if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    buttons.setup()
    rotary.setup()

    display_welcome()

    connect_xplane()
    input("Press enter to quit\n")
    GPIO.cleanup()
