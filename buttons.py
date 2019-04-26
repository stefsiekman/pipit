import time
import RPi.GPIO as GPIO


leds = {
    "A": 22,
    "B": 8,
    "E": 11,
    "F": 24
}

buttons = {
    "A": 9,
    "B": 23,
    "E": 10,
    "F": 25
}


def process_button_pressed(channel):
    print(f"Button on {channel} pressed")


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
        time.sleep(0.25)
        GPIO.output(pin, False)
        time.sleep(0.1)

    # Flash all at once
    all_pins = tuple(leds.values())
    GPIO.output(all_pins, True)
    time.sleep(1)
    GPIO.output(all_pins, False)


