import RPi.GPIO as GPIO

gray_codes = [(1, 1), (1, 0), (0, 0), (0, 1)]

pins = (
    (17, 27),
    (4, 14)
)

handler = None


def code_relative(code, offset):
    return gray_codes[(gray_codes.index(code) + offset) % 4]


def read_pins(encoder):
    return GPIO.input(pins[encoder][0]), GPIO.input(pins[encoder][1])


last_state = [
    (1, 1),
    (1, 1),
]


def pin_changed(channel):
    global last_state

    #    print("Pin changed (rotary)")

    if handler is None:
        return

    encoder = 0 if channel in pins[0] else 1

    new_state = read_pins(encoder)
    if new_state == last_state[encoder]:
        return
    if last_state[encoder] == (1, 0) and new_state == (0, 0):
        handler(encoder, 1)
    elif last_state[encoder] == (0, 1) and new_state == (0, 0):
        handler(encoder, -1)

    last_state[encoder] = new_state


def setup(the_handler):
    global handler

    handler = the_handler

    for pin_set in pins:
        GPIO.setup(pin_set, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        for pin in pin_set:
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=pin_changed,
                                  bouncetime=3)


def unregister():
    for pin_set in pins:
        for pin in pin_set:
            GPIO.remove_event_detect(pin)
