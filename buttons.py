import time
import RPi.GPIO as GPIO


leds = {
    "A": 22,
    "B": 8,
    "C": 7,
    "D": 6,
    "E": 11,
    "F": 24,
    "G": 12,
    "H": 0,
}

buttons = {
    "A": 9,
    "B": 23,
    "C": 16,
    "D": 13,
    "E": 10,
    "F": 25,
    "G": 1,
    "H": 5,
    "L": 18,
    "R": 15,
    "X": 21,
    "Y": 26,
    "Z": 20,
    "W": 19
}

handler = None


def process_button_pressed(channel):
    if handler is None:
        return

    for button, pin in buttons.items():
        if pin == channel:
            handler(button)


def setup(the_handler):
    global handler

    handler = the_handler
    
    GPIO.setup(tuple(leds.values()), GPIO.OUT)
    GPIO.setup(tuple(buttons.values()), GPIO.IN, pull_up_down=GPIO.PUD_UP)
    for pin in buttons.values():
        GPIO.add_event_detect(pin, GPIO.FALLING, process_button_pressed,
                              bouncetime=250)


def flash():
    # Blink all in sequence
    leds_blinked = 0
    for pin in leds.values():
        GPIO.output(pin, True)
        time.sleep(0.05)
        GPIO.output(pin, False)

        leds_blinked += 1
        if leds_blinked != len(leds):
            time.sleep(0.05)

    # Flash all at once
    all_pins = tuple(leds.values())
    GPIO.output(all_pins, True)
    time.sleep(1)
    GPIO.output(all_pins, False)


def clear():
    for pin in leds.values():
        GPIO.output(pin, False)
