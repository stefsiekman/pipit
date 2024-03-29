import abc
import RPi.GPIO as GPIO

import buttons
import refs

KEY_IAS_HDG = "ias-hdg"
KEY_ALTITUDE = "alt"
KEY_COURSE = "course"
KEY_COM = "com"
KEY_NAV = "nav"


class ScreenState(abc.ABC):

    all_button_map = {
        "C": refs.CMD_PRESS_CMD_A,
        "D": refs.CMD_PRESS_CMD_B,
    }

    all_led_map = {
        refs.REF_STATUS_CMD_A: buttons.leds["C"],
        refs.REF_STATUS_CMD_B: buttons.leds["D"],
    }

    @abc.abstractmethod
    def init_display(self):
        GPIO.output(buttons.leds["A"], False)
        GPIO.output(buttons.leds["B"], False)
        GPIO.output(buttons.leds["E"], False)
        GPIO.output(buttons.leds["F"], False)

    @abc.abstractmethod
    def input(self, source, val):
        if source in self.all_button_map:
            refs.send_command(self.all_button_map[source])
        elif source == "X":
            return KEY_IAS_HDG
        elif source == "Y":
            return KEY_ALTITUDE
        elif source == "Z":
            return KEY_COURSE
        elif source == "W":
            return KEY_COM
        else:
            print(f"Unhandled input source: {source}")

    @abc.abstractmethod
    def ref_changed(self, ref, new_value):
        if ref in self.all_led_map:
            print(f"Changing ref {ref} on {self.all_led_map[ref]} to {bool(new_value)}")
            GPIO.output(self.all_led_map[ref], bool(new_value))


class SpeedHeadingState(ScreenState):

    button_map = {
        "A": refs.CMD_PRESS_VNAV,
        "B": refs.CMD_PRESS_LNAV,
        "E": refs.CMD_PRESS_SPEED,
        "F": refs.CMD_PRESS_HDG_SEL,
    }

    led_map = {
        refs.REF_STATUS_VNAV: buttons.leds["A"],
        refs.REF_STATUS_LNAV: buttons.leds["B"],
        refs.REF_STATUS_SPEED: buttons.leds["E"],
        refs.REF_STATUS_HDG_SEL: buttons.leds["F"],
    }

    def __init__(self, lcd):
        self.lcd = lcd

    def init_display(self):
        self.lcd.clear()
        self.lcd.cursor_pos = 0, 6
        self.lcd.write_string("IAS / MACH")
        self.lcd.cursor_pos = 1, 6
        self.lcd.write_string("HEADING")
        
        super(SpeedHeadingState, self).init_display()

        for ref in [refs.REF_AIRSPEED, refs.REF_HEADING] + list(self.led_map.keys()):
            self.ref_changed(ref, refs.current_value(ref))

    def ref_changed(self, ref, new_val):
        if ref == refs.REF_AIRSPEED:
            self.lcd.cursor_pos = 0, 0
            speed_string = f" {int(new_val or 0):03d}"
            if new_val is not None and new_val < 1:
                speed_string = f"{new_val:.2f} "[1:]
            self.lcd.write_string(speed_string)
        elif ref == refs.REF_HEADING:
            self.lcd.cursor_pos = 1, 1
            self.lcd.write_string(f"{int(new_val or 0):03d}")
        elif ref == refs.REF_DIGIT_8:
            self.lcd.cursor_pos = 0, 0
            self.lcd.write_string("8" if new_val else " ")
        elif ref == refs.REF_DIGIT_A:
            self.lcd.cursor_pos = 0, 0
            self.lcd.write_string("A" if new_val else " ")
        elif ref in self.led_map:
            GPIO.output(self.led_map[ref], bool(new_val))
        else:
            super(SpeedHeadingState, self).ref_changed(ref, new_val)

    def input(self, source, val=None):
        if source == "LR":
            refs.send_command(refs.CMD_AIRSPEED_UP
                              if val > 0 else refs.CMD_AIRSPEED_DOWN, True)
        elif source == "RR":
            refs.send_command(refs.CMD_HEADING_UP
                              if val > 0 else refs.CMD_HEADING_DOWN, True)
        elif source in self.button_map:
            refs.send_command(self.button_map[source])
        else:
            return super(SpeedHeadingState, self).input(source, val)


class CourseState(ScreenState):

    button_map = {
        "A": refs.CMD_PRESS_VOR_LOC,
        "B": refs.CMD_PRESS_APP,
    }

    led_map = {
        refs.REF_STATUS_VOR_LOC: buttons.leds["A"],
        refs.REF_STATUS_APP: buttons.leds["B"],
    }

    def __init__(self, lcd):
        self.lcd = lcd

    def init_display(self):
        self.lcd.clear()
        self.lcd.cursor_pos = 0, 6
        self.lcd.write_string("COURSE CPT")
        self.lcd.cursor_pos = 1, 6
        self.lcd.write_string("COURSE F/O")
        
        super(CourseState, self).init_display()

        for ref in [refs.REF_COURSE_CPT, refs.REF_COURSE_FO] + list(self.led_map.keys()):
            self.ref_changed(ref, refs.current_value(ref))

    def ref_changed(self, ref, new_val):
        if ref == refs.REF_COURSE_CPT:
            self.lcd.cursor_pos = 0, 0
            self.lcd.write_string(f"{int(new_val):3d}")
        elif ref == refs.REF_COURSE_FO:
            self.lcd.cursor_pos = 1, 0
            self.lcd.write_string(f"{int(new_val):3d}")
        elif ref in self.led_map:
            GPIO.output(self.led_map[ref], bool(new_val))
        else:
            super(CourseState, self).ref_changed(ref, new_val)

    def input(self, source, val=None):
        if source == "LR":
            refs.send_command(refs.CMD_COURSE_CPT_UP if val > 0 else
                              refs.CMD_COURSE_CPT_DOWN, True)
        elif source == "RR":
            refs.send_command(
                refs.CMD_COURSE_FO_UP if val > 0 else
                refs.CMD_COURSE_FO_DOWN, True)
        elif source in self.button_map:
            refs.send_command(self.button_map[source])
        else:
            return super(CourseState, self).input(source, val)


class AltitudeState(ScreenState):

    button_map = {
        "A": refs.CMD_PRESS_AT,
        "B": refs.CMD_PRESS_ALT_HLD,
        "E": refs.CMD_PRESS_LVL_CHG,
        "F": refs.CMD_PRESS_VS,
    }

    led_map = {
        refs.REF_STATUS_AT: buttons.leds["A"],
        refs.REF_STATUS_ALT_HLD: buttons.leds["B"],
        refs.REF_STATUS_LVL_CHG: buttons.leds["E"],
        refs.REF_STATUS_VS: buttons.leds["F"],
    }

    def __init__(self, lcd):
        self.lcd = lcd

    def init_display(self):
        self.lcd.clear()
        self.lcd.cursor_pos = 0, 6
        self.lcd.write_string("ALTITUDE")
        self.lcd.cursor_pos = 1, 6
        self.lcd.write_string("VERT SPEED")
        
        super(AltitudeState, self).init_display()

        for ref in [refs.REF_ALTITUDE, refs.REF_VERTICAL_SPEED] + list(self.led_map.keys()):
            self.ref_changed(ref, refs.current_value(ref))

    def ref_changed(self, ref, new_val):
        if ref == refs.REF_ALTITUDE:
            self.lcd.cursor_pos = 0, 0
            self.lcd.write_string(f"{int(new_val):5d}")
        elif ref == refs.REF_VERTICAL_SPEED:
            self.lcd.cursor_pos = 1, 0
            if new_val != 0:
                self.lcd.write_string("-" if new_val < 0 else "+")
                self.lcd.write_string(f"{abs(int(new_val)):4d}")
            else:
                self.lcd.write_string("     ")
        elif ref in self.led_map:
            GPIO.output(self.led_map[ref], bool(new_val))
        else:
            super(AltitudeState, self).ref_changed(ref, new_val)

    def input(self, source, val=None):
        if source == "LR":
            refs.send_command(refs.CMD_ALTITUDE_UP if val > 0 else
                              refs.CMD_ALTITUDE_DOWN, True)
        elif source == "RR":
            refs.send_command(
                refs.CMD_VERTICAL_SPEED_UP if val > 0 else
                refs.CMD_VERTICAL_SPEED_DOWN)
        elif source in self.button_map:
            refs.send_command(self.button_map[source])
        else:
            return super(AltitudeState, self).input(source, val)


class ComState(ScreenState):

    button_map = {
        "H": refs.CMD_COM_FLIP
    }

    led_map = {
    }

    def __init__(self, lcd):
        self.lcd = lcd

    def init_display(self):
        self.lcd.cursor_pos = 0, 7
        self.lcd.write_string(" COM ACT ")
        self.lcd.cursor_pos = 1, 7
        self.lcd.write_string(" COM STBY")
        
        super(ComState, self).init_display()

        for ref in [refs.REF_COM_ACT, refs.REF_COM_STDBY]:
            self.ref_changed(ref, refs.current_value(ref))

    def ref_changed(self, ref, new_val):
        if ref == refs.REF_COM_ACT:
            self.lcd.cursor_pos = 0, 0
            self.lcd.write_string(f"{new_val/100:3.3f}")
        if ref == refs.REF_COM_STDBY:
            self.lcd.cursor_pos = 1, 0
            self.lcd.write_string(f"{new_val/100:3.3f}")
        elif ref in self.led_map:
            GPIO.output(self.led_map[ref], bool(new_val))

    def input(self, source, val=None):
        if source == "LR":
            refs.send_command(refs.CMD_COM_COARSE_UP if val > 0 else
                              refs.CMD_COM_COARSE_DOWN)
        elif source == "RR":
            refs.send_command(refs.CMD_COM_FINE_UP if val > 0 else
                              refs.CMD_COM_FINE_DOWN)
        elif source in self.button_map:
            refs.send_command(self.button_map[source])
        elif source == "W":
            return KEY_NAV
        else:
            return super(ComState, self).input(source, val)


class NavState(ScreenState):
    
    NAV_REFS = {
        1: {
            "act": refs.REF_NAV1_ACT,
            "stdby": refs.REF_NAV1_STDBY,
            "coarse_up": refs.CMD_NAV1_COARSE_UP,
            "coarse_down": refs.CMD_NAV1_COARSE_DOWN,
            "fine_up": refs.CMD_NAV1_FINE_UP,
            "fine_down": refs.CMD_NAV1_FINE_DOWN,
            "flip": refs.CMD_NAV1_FLIP,
        },
        2: {
            "act": refs.REF_NAV2_ACT,
            "stdby": refs.REF_NAV2_STDBY,
            "coarse_up": refs.CMD_NAV2_COARSE_UP,
            "coarse_down": refs.CMD_NAV2_COARSE_DOWN,
            "fine_up": refs.CMD_NAV2_FINE_UP,
            "fine_down": refs.CMD_NAV2_FINE_DOWN,
            "flip": refs.CMD_NAV2_FLIP,
        },
    }

    current_side = 1

    def __init__(self, lcd):
        self.lcd = lcd
        
    def init_display(self):
        self.lcd.cursor_pos = 0, 7
        self.lcd.write_string(f" NAV{self.current_side}ACT")
        self.lcd.cursor_pos = 1, 7
        self.lcd.write_string(f" NAV{self.current_side}STBY")
        
        super(NavState, self).init_display()
        
        # G & H leds are too broken to be used :(
        # GPIO.output(buttons.leds["H"], bool(self.current_side - 1))

        for ref in [self.ref("act"), self.ref("stdby")]:
            self.ref_changed(ref, refs.current_value(ref))
            
    def ref(self, ref):
        return self.NAV_REFS[self.current_side][ref]
            
    def change_side(self):
        self.current_side = (self.current_side % 2) + 1
        self.init_display()

    def ref_changed(self, ref, new_val):
        if ref == self.ref("act"):
            self.lcd.cursor_pos = 0, 0
            self.lcd.write_string(f"{new_val/100:3.2f}")
        if ref == self.ref("stdby"):
            self.lcd.cursor_pos = 1, 0
            self.lcd.write_string(f"{new_val/100:3.2f}")

    def input(self, source, val=None):
        if source == "LR":
            refs.send_command(self.ref("coarse_up") if val > 0 else
                              self.ref("coarse_down"))
        elif source == "RR":
            refs.send_command(self.ref("fine_up") if val > 0 else
                              self.ref("fine_down"))
        elif source == "G":
            refs.send_command(self.ref("flip"))
        elif source == "H":
            self.change_side()
        elif source == "W":
            return KEY_COM
        else:
            return super(NavState, self).input(source, val)


