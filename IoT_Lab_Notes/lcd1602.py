# =============================================================================
#  lcd1602.py - DRIVER FOR THE GROVE 16x2 I2C LCD (from Brightspace)
#  Commented copy for revision. Copy this file to the Pico with EXACTLY this
#  name, then:   from lcd1602 import LCD1602
# =============================================================================
#
#  HOW TO USE (all you need for the lab / lab test):
#
#     from machine import I2C, Pin
#     from lcd1602 import LCD1602
#     i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100_000)
#     lcd = LCD1602(i2c, 2, 0)      # 2 lines, dotsize 0 (5x8 font)
#     lcd.clear()                   # wipe screen, cursor to (0,0) - SLOW (2ms)
#     lcd.setCursor(0, 0)           # (column 0..15, row 0..1)
#     lcd.print('Hello')            # write text at the cursor
#     lcd.setCursor(0, 1)
#     lcd.print('Row two')
#
#  TIPS
#  * Only 16 characters fit per row. Extra characters go off-screen into
#    hidden display memory - they do NOT wrap onto row 2.
#  * lcd.print() does not erase what was there. To overwrite a shorter
#    value, pad it: lcd.print('{:<16}'.format(text))  (left-align to 16).
#    This is also faster and flickers less than calling clear() each time.
#  * Only ASCII prints correctly. '°' won't show - write 'C' or use
#    lcd.write(0xDF), the LCD's built-in degree symbol.
#  * If you get OSError: [Errno 5] EIO -> wrong pins, loose cable, or the
#    LCD isn't powered. Check with print(i2c.scan()) -> should include
#    62 (0x3E). The RGB-backlit version also shows 98 (0x62).
#
#  HOW IT WORKS (week 10 lecture "command + data" pattern)
#  Every I2C message to the LCD (address 0x3E) starts with a control byte:
#     0x80 -> the next byte is a COMMAND for the HD44780 controller
#     0x40 -> the next byte is a CHARACTER (data) to display
#  writeto_mem(addr, 0x80, b'\x01') == "send command 0x01 (clear)".
# =============================================================================

from machine import I2C, Pin
import time


class LCD1602(object):
    # ---- HD44780 command bytes (sent after the 0x80 control byte) ----
    LCD_CLEARDISPLAY = 0x01     # clear screen + cursor home
    LCD_RETURNHOME = 0x02       # cursor to (0, 0)
    LCD_ENTRYMODESET = 0x04     # text direction / shifting (OR with flags)
    LCD_DISPLAYCONTROL = 0x08   # display/cursor/blink on-off (OR with flags)
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20      # lines, font size, bus width
    LCD_SETCGRAMADDR = 0x40     # custom character memory
    LCD_SETDDRAMADDR = 0x80     # set cursor position (0b1RCCCCCCC)

    # flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

    # flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    def __init__(self, i2c, lines, dotsize, lcd_addr=0x3E):
        """i2c: a machine.I2C object. lines: 1 or 2. dotsize: 0 = 5x8 font.
        lcd_addr: 0x3E for the Grove LCD."""
        self.i2c = i2c
        self.lcd_address = lcd_addr
        self.line = lines
        self.currline = 0
        self.display_control = self.LCD_DISPLAYON
        if (lines > 1):
            self.display_control |= self.LCD_2LINE
        # for some 1 line displays you can select a 10 pixel high font
        if (dotsize != 0 & lines == 1):
            self.display_control |= self.LCD_5x10DOTS

        # Power-up sequence from the Hitachi HD44780 datasheet (p45/46):
        # wait >40ms after power reaches 2.7V before sending commands.
        time.sleep_ms(50)

        # Send "function set" three times with delays (datasheet fig. 23)
        self.command(self.LCD_FUNCTIONSET | self.display_control)
        time.sleep_us(4500)     # wait more than 4.1ms
        self.command(self.LCD_FUNCTIONSET | self.display_control)
        time.sleep_us(150)
        self.command(self.LCD_FUNCTIONSET | self.display_control)
        # finally, set # lines, font size, etc.
        self.command(self.LCD_FUNCTIONSET | self.display_control)

        # turn the display on with no cursor or blinking by default
        self.display_mode = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        self.display()
        self.clear()

        # Default text direction: left to right
        self.display_mode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
        self.command(self.LCD_ENTRYMODESET | self.display_mode)

    def clear(self):
        """Clear the screen and put the cursor at (0,0). Takes ~2ms."""
        self.command(self.LCD_CLEARDISPLAY)
        time.sleep_ms(2)        # this command takes a long time!

    def home(self):
        """Cursor to (0,0) without clearing."""
        self.command(self.LCD_RETURNHOME)
        time.sleep_ms(2)

    def setCursor(self, col, row):
        """Move cursor. col 0..15, row 0 (top) or 1 (bottom).
        Row 0 starts at display address 0x00 -> command 0x80 | col
        Row 1 starts at display address 0x40 -> command 0xC0 | col
        (0x80 = 'set address' bit, 0x40 = start of second row)."""
        col = (col | 0x80) if row == 0 else (col | 0xc0)
        self.command(col)

    # ---- display on/off (quickly, keeps the text) ----
    def no_display(self):
        self.display_control &= ~self.LCD_DISPLAYON
        self.command(self.LCD_DISPLAYCONTROL | self.display_control)

    def display(self):
        self.display_control |= self.LCD_DISPLAYON
        self.command(self.LCD_DISPLAYCONTROL | self.display_control)

    # ---- underline cursor on/off ----
    def no_cursor(self):
        self.display_control &= ~self.LCD_CURSORON
        self.command(self.LCD_DISPLAYCONTROL | self.display_control)

    def cursor(self):
        self.display_control |= self.LCD_CURSORON
        self.command(self.LCD_DISPLAYCONTROL | self.display_control)

    # ---- blinking cursor on/off ----
    def no_blink(self):
        self.display_control &= ~self.LCD_BLINKON
        self.command(self.LCD_DISPLAYCONTROL | self.display_control)

    def blink(self):
        self.display_control |= self.LCD_BLINKON
        self.command(self.LCD_DISPLAYCONTROL | self.display_control)

    # NOTE: autoscroll()/no_autoscroll() in the original driver send the
    # flag with the DISPLAYCONTROL command instead of ENTRYMODESET, so they
    # don't really autoscroll (and toggle blink instead). For scrolling text
    # (Lab 10) slice the string yourself - see week10 file.
    def autoscroll(self):
        self.display_control |= self.LCD_ENTRYSHIFTINCREMENT
        self.command(self.LCD_DISPLAYCONTROL | self.display_control)

    def no_autoscroll(self):
        self.display_control &= ~self.LCD_ENTRYSHIFTINCREMENT
        self.command(self.LCD_DISPLAYCONTROL | self.display_control)

    def create_char(self, location, charmap):
        """Define custom character 0..7 from 8 row bitmasks (5 bits each),
        then display it with lcd.write(location).
        (Fixed: the original referenced LCD_SETCGRAMADDR and self.address
        without `self.`/the right name, so it crashed.)"""
        location &= 0x07
        self.command(self.LCD_SETCGRAMADDR | (location << 3))
        for row in charmap:
            self.i2c.writeto_mem(self.lcd_address, 0x40, bytearray([row]))

    def command(self, command):
        """Send one command byte: control byte 0x80 then the command."""
        command = bytearray([command])
        self.i2c.writeto_mem(self.lcd_address, 0x80, command)

    def write(self, command):
        """Send one character code: control byte 0x40 then the char."""
        command = bytearray([command])
        self.i2c.writeto_mem(self.lcd_address, 0x40, command)

    def print(self, text):
        """Write a string at the current cursor position."""
        for char in text:
            self.write(ord(char))


class LCD1602_RGB(LCD1602):
    """Version with a colour backlight (second I2C chip at 0x62).
    lcd = LCD1602_RGB(i2c, 2, 0); lcd.set_rgb(255, 0, 0)  # red backlight"""
    # color define
    WHITE = 0
    RED = 1
    GREEN = 2
    BLUE = 3

    REG_RED = 0x04        # pwm2
    REG_GREEN = 0x03      # pwm1
    REG_BLUE = 0x02       # pwm0

    REG_MODE1 = 0x00
    REG_MODE2 = 0x01
    REG_OUTPUT = 0x08

    def __init__(self, i2c, lines, dotsize, lcd_addr=0x3E, rgb_addr=0x62):
        self.rgb_address = rgb_addr
        LCD1602.__init__(self, i2c, lines, dotsize, lcd_addr)

        # backlight init
        self.set_reg(0, 0)
        self.set_reg(1, 0)
        self.set_reg(0x08, 0xAA)  # all led control by pwm
        self.set_rgb(255, 255, 255)

    def set_reg(self, addr, value):
        value = bytearray([value])
        self.i2c.writeto_mem(self.rgb_address, addr, bytearray([]))
        self.i2c.writeto_mem(self.rgb_address, addr, value)

    def set_rgb(self, red, green, blue):
        """Backlight colour, each 0..255."""
        r = int(red)
        g = int(green)
        b = int(blue)
        self.set_reg(self.REG_RED, r)
        self.set_reg(self.REG_GREEN, g)
        self.set_reg(self.REG_BLUE, b)

    def set_color(self, color):
        """Preset colours: 0 white, 1 red, 2 green, 3 blue."""
        if (color == 0):
            self.set_rgb(255, 255, 255)
        elif (color == 1):
            self.set_rgb(255, 0, 0)
        elif (color == 2):
            self.set_rgb(0, 255, 0)
        elif (color == 3):
            self.set_rgb(0, 0, 255)
        else:
            return
