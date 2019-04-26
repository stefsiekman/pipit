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


def process_button_pressed(channel):
    for button, pin in buttons.items():
        if pin == channel:
            print(f"Button {button} pressed")


def setup():
    GPIO.setup(tuple(leds.values()), GPIO.OUT)
    GPIO.setup(tuple(buttons.values()), GPIO.IN, pull_up_down=GPIO.PUD_UP)
    for pin in buttons.values():
        GPIO.add_event_detect(pin, GPIO.FALLING, process_button_pressed,
                              bouncetime=250)


def flash():
    # Blink all in sequence
    for pin in leds.values():
        GPIO.output(pin, True)
        time.sleep(0.15)
        GPIO.output(pin, False)
        time.sleep(0.05)

    # Flash all at once
    all_pins = tuple(leds.values())
    GPIO.output(all_pins, True)
    time.sleep(1)
    GPIO.output(all_pins, False)


