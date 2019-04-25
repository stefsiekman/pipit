import time
import RPLCD.i2c as CharLCD

def setup_lcd():
    return CharLCD("...", 0x3f)

def display_welcome(lcd):
    lcd.clear()
    lcd.cursor_pos = 0, 5
    lcd.write_string("PiPit")
    lcd.cursor_pos = 1, 4
    lcd.write_string("Welcome")
    time.sleep(1)


if __name__ == "__main__":
    lcd = setup_lcd()
    display_welcome(lcd)
