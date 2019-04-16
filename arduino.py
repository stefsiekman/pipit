import serial

s = None


def setup():
    global s

    s = serial.Serial(port="/dev/cu.usbmodem143101", baudrate=9600)

def set_led(on):
    global s

    s.write(b"on\n" if on else b"off\n")
    s.flush()
