import time
from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO

import buttons
import refs
import rotary
import beacon
import states


lcd = CharLCD("PCF8574", 0x3f)


all_states = {
    states.KEY_IAS_HDG: states.SpeedHeadingState(lcd),
    states.KEY_ALTITUDE: states.AltitudeState(lcd),
    states.KEY_COM: states.ComState(lcd),
    states.KEY_NAV: states.NavState(lcd),
    states.KEY_COURSE: states.CourseState(lcd),
}
current_state_key = states.KEY_IAS_HDG


def current_state():
    return all_states[current_state_key]


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
        time.sleep(1)
        return
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
    current_state().ref_changed(ref, new_val)


def setup_refs():
    refs.set_handler(ref_changed)
    refs.request_all()
    current_state().init_display()
    refs.start_thread()


def delegate_input(source, value=None):
    global current_state_key

    new_state = current_state().input(source, value)
    if new_state in all_states:
        current_state_key = new_state
        current_state().init_display()


def button_pressed(button):
    delegate_input(button)


def rotary_turned(encoder, direction):
    delegate_input("LR" if encoder == 0 else "RR", direction)


def has_xplane_connection():
    return refs.installation_is_setup()


if __name__ == "__main__":
    print("Welcome to PiPit")

    GPIO.setmode(GPIO.BCM)
    buttons.setup(button_pressed)
    rotary.setup(rotary_turned)

    display_welcome()

    while True:
        connect_xplane()

        if has_xplane_connection():
            break

    setup_refs()

    # Run for 1 year
    time.sleep(365 * 24 * 60 * 60)
    refs.stop_connection()
    lcd.clear()
    buttons.clear()
    GPIO.cleanup()
