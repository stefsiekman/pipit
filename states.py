import abc
import refs


class ScreenState(abc.ABC):

    @abc.abstractmethod
    def init_display(self):
        pass

    @abc.abstractmethod
    def input(self, source, val):
        pass


class SpeedHeadingState(ScreenState):

    button_map = {
        "A": refs.CMD_PRESS_LNAV,
        "B": refs.CMD_PRESS_VNAV,
        "F": refs.CMD_PRESS_HDG_SEL,
    }

    def __init__(self, lcd):
        self.lcd = lcd
        
    def init_display(self):
        self.lcd.clear()
        self.lcd.cursor_pos = 0, 0
        self.lcd.write_string("AIS")
        self.lcd.cursor_pos = 1, 0
        self.lcd.write_string("HDG")

    def input(self, source, val=None):
        if source == "LR":
            refs.send_command(
                refs.CMD_AIRSPEED_UP if val > 0 else refs.CMD_AIRSPEED_DOWN)
        elif source == "RR":
            refs.send_command(
                refs.CMD_HEADING_UP if val > 0 else refs.CMD_HEADING_DOWN)
        elif source in self.button_map:
            refs.send_command(self.button_map[source])

