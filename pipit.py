import time
from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO

import buttons
import refs
import rotary
import beacon


lcd = CharLCD("PCF8574", 0x3f)

button_map = {
    "A": refs.CMD_PRESS_LNAV,
    "B": refs.CMD_PRESS_VNAV,
    "F": refs.CMD_PRESS_HDG_SEL,
}

led_map = {
    refs.REF_STATUS_HDG_SEL: buttons.leds["F"]
}


def display_welcome():
    lcd.clear()
    lcd.cursor_pos = 0, 5
    lcd.write_string("PiPit")
    # time.sleep(0.5)
    lcd.cursor_pos = 1, 4
    lcd.write_string("Welcome")
    # time.sleep(0.5)
    lcd.clear()

    lcd.cursor_pos = 0, 0
    lcd.write_string("Testing LEDs...")

    # buttons.flash()

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

    refs.setup_installation(beacon_info)

    time.sleep(0.75)
    lcd.clear()
    lcd.cursor_pos = 0, 4
    lcd.write_string("Hostname")
    lcd.cursor_pos = 1, 0
    lcd.write_string(beacon_info[2])
    
    # time.sleep(2)


def ref_changed(ref, old_val, new_val):
    if ref == refs.REF_AIRSPEED:
        lcd.cursor_pos = 0, 5
        lcd.write_string(f"{int(new_val):03d}")
    elif ref == refs.REF_HEADING:
        lcd.cursor_pos = 1, 5
        lcd.write_string(f"{int(new_val):03d}")
    elif ref in led_map:
        GPIO.output(led_map[ref], bool(new_val))


def setup_refs():
    refs.set_handler(ref_changed)
    refs.request(30, [
        refs.REF_AIRSPEED,
        refs.REF_HEADING,
        refs.REF_STATUS_HDG_SEL,
        refs.REF_STATUS_LNAV,
        refs.REF_STATUS_VNAV,
    ])

    lcd.clear()
    lcd.cursor_pos = 0, 0
    lcd.write_string("AIS")
    lcd.cursor_pos = 1, 0
    lcd.write_string("HDG")

    refs.start_thread()


def button_pressed(button):
    if button in button_map:
        refs.send_command(button_map[button])


def rotary_turned(encoder, direction):
    if encoder == 0:
        refs.send_command(
            refs.CMD_AIRSPEED_UP if direction > 0 else refs.CMD_AIRSPEED_DOWN)
    if encoder == 1:
        refs.send_command(
            refs.CMD_HEADING_UP if direction > 0 else refs.CMD_HEADING_DOWN)


if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    buttons.setup(button_pressed)
    rotary.setup(rotary_turned)

    display_welcome()
    connect_xplane()
    setup_refs()

    input("Press enter to quit\n")
    refs.stop_connection()
    lcd.clear()
    buttons.clear()
    GPIO.cleanup()
