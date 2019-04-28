import abc
import RPi.GPIO as GPIO

import buttons
import refs

KEY_IAS_HDG = "ias-hdg"


class ScreenState(abc.ABC):

    @abc.abstractmethod
    def init_display(self):
        pass

    @abc.abstractmethod
    def input(self, source, val):
        print(f"Unhandled input source: {source}")

    @abc.abstractmethod
    def ref_changed(self, ref, new_value):
        pass


class SpeedHeadingState(ScreenState):

    button_map = {
        "A": refs.CMD_PRESS_LNAV,
        "B": refs.CMD_PRESS_VNAV,
        "F": refs.CMD_PRESS_HDG_SEL,
    }

    led_map = {
        refs.REF_STATUS_HDG_SEL: buttons.leds["F"]
    }

    def __init__(self, lcd):
        self.lcd = lcd
        
    def init_display(self):
        self.lcd.clear()
        self.lcd.cursor_pos = 0, 0
        self.lcd.write_string("IAS")
        self.lcd.cursor_pos = 1, 0
        self.lcd.write_string("HDG")

    def ref_changed(self, ref, new_val):
        if ref == refs.REF_AIRSPEED:
            self.lcd.cursor_pos = 0, 5
            self.lcd.write_string(f"{int(new_val):03d}")
        elif ref == refs.REF_HEADING:
            self.lcd.cursor_pos = 1, 5
            self.lcd.write_string(f"{int(new_val):03d}")
        elif ref in self.led_map:
            GPIO.output(self.led_map[ref], bool(new_val))

    def input(self, source, val=None):
        if source == "LR":
            refs.send_command(
                refs.CMD_AIRSPEED_UP if val > 0 else refs.CMD_AIRSPEED_DOWN)
        elif source == "RR":
            refs.send_command(
                refs.CMD_HEADING_UP if val > 0 else refs.CMD_HEADING_DOWN)
        elif source in self.button_map:
            refs.send_command(self.button_map[source])
        else:
            super(SpeedHeadingState, self).input(source, val)


