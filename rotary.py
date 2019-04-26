import RPi.GPIO as GPIO


pins = (
    (17, 27),
    (4, 14)
)


def setup():
    for pin_set in pins:
        GPIO.setup(pin_set, GPIO.IN, pull_up_down=GPIO.PUD_UP)
