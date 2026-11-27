# =============================================================================
#  LAB TEST PRACTICE - PAST PAPERS 2022, 2023, 2024 DONE ON THE PICO
#  Runs on: PICO WH with the Grove LCD (needs lcd1602.py)
# =============================================================================
#  The old lab tests used an Arduino. These are the same tasks on the Pico.
#  Set PAPER below and run.
#
#  TRICKS USED (handy for any lab test)
#  * Detect a button PRESS (not hold): compare with last loop's value.
#        if button.value() == 1 and last == 0:   -> just pressed
#  * Never use long sleeps - keep the loop fast so buttons always respond.
#  * Write a full 16-character line on the LCD so old text is wiped:
#        lcd.print('{:<16}'.format(text))
# =============================================================================

import time
from machine import Pin, PWM, ADC, I2C
from lcd1602 import LCD1602

PAPER = 2022                      # 2022, 2023 or 2024

i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100_000)
lcd = LCD1602(i2c, 2, 0)


def show(row, text):
    lcd.setCursor(0, row)
    lcd.print('{:<16}'.format(text))      # pad to 16 characters


# =============================================================================
#  2022 - THERMOMETER
#  Top row: current temperature. Bottom row: minimum since power on.
#  Button 1: switch bottom row between minimum and maximum.
#  Button 2: switch everything between Celsius and Fahrenheit.
#  Show whole numbers, rounded to the nearest (69.8 -> 70).
# =============================================================================
def paper_2022():
    button1 = Pin(16, Pin.IN, Pin.PULL_DOWN)
    button2 = Pin(18, Pin.IN, Pin.PULL_DOWN)
    sensor = ADC(4)

    lowest = 100
    highest = -100
    show_max = False
    fahrenheit = False
    last1 = 0
    last2 = 0

    while True:
        voltage = sensor.read_u16() * 3.3 / 65536
        temp = 27 - (voltage - 0.706) / 0.001721
        lowest = min(lowest, temp)
        highest = max(highest, temp)

        # Toggle only on the moment the button goes down
        if button1.value() == 1 and last1 == 0:
            show_max = not show_max
        if button2.value() == 1 and last2 == 0:
            fahrenheit = not fahrenheit
        last1 = button1.value()
        last2 = button2.value()

        if show_max:
            label, other = 'Max', highest
        else:
            label, other = 'Min', lowest

        if fahrenheit:
            # int(x + 0.5) rounds to nearest. (Python's round() rounds
            # 68.5 down to 68, so avoid it here.)
            show(0, 'Temp: ' + str(int(temp * 9 / 5 + 32 + 0.5)) + 'F')
            show(1, label + ': ' + str(int(other * 9 / 5 + 32 + 0.5)) + 'F')
        else:
            show(0, 'Temp: ' + str(int(temp + 0.5)) + 'C')
            show(1, label + ': ' + str(int(other + 0.5)) + 'C')

        time.sleep_ms(50)


# =============================================================================
#  2023 - MOOD LAMP
#  Three potentiometers set the red, green and blue of an RGB LED.
#  Top row shows the colour in hex, e.g. #FF8800.
#  Button 1: save the current colour as the favourite.
#  Button 2: switch to "Favourite" mode (shows saved colour; pots and
#            button 1 do nothing). Press again to go back to
#            "Potentiometer" mode. Does nothing if no favourite saved.
#  Holding button 2 must not keep switching.
# =============================================================================
def paper_2023():
    pot_r, pot_g, pot_b = ADC(0), ADC(1), ADC(2)        # GP26, GP27, GP28
    led_r = PWM(Pin(13), freq=1000)
    led_g = PWM(Pin(14), freq=1000)
    led_b = PWM(Pin(15), freq=1000)
    button1 = Pin(16, Pin.IN, Pin.PULL_DOWN)
    button2 = Pin(18, Pin.IN, Pin.PULL_DOWN)

    favourite = None
    favourite_mode = False
    last1 = 0
    last2 = 0

    while True:
        press1 = button1.value() == 1 and last1 == 0
        press2 = button2.value() == 1 and last2 == 0
        last1 = button1.value()
        last2 = button2.value()

        if favourite_mode:
            r, g, b = favourite
            if press2:
                favourite_mode = False
        else:
            # read_u16() gives 0..65535; // 256 turns it into 0..255
            r = pot_r.read_u16() // 256
            g = pot_g.read_u16() // 256
            b = pot_b.read_u16() // 256
            if press1:
                favourite = (r, g, b)
            if press2 and favourite is not None:
                favourite_mode = True

        # 0..255 -> 0..65535 for PWM
        led_r.duty_u16(r * 257)
        led_g.duty_u16(g * 257)
        led_b.duty_u16(b * 257)

        # {:02X} = 2-digit uppercase hex, e.g. 255 -> FF, 8 -> 08
        show(0, '#{:02X}{:02X}{:02X}'.format(r, g, b))
        if favourite_mode:
            show(1, 'Favourite')
        else:
            show(1, 'Potentiometer')

        time.sleep_ms(50)


# =============================================================================
#  2024 - PAN/TILT CAMERA WITH TWO SERVOS
#  Type commands in the Thonny shell:  X100;  or  Y20;
#  X or Y, then up to 3 digits, then ';'. Anything else is ignored.
#  Both servos can move at the same time, and new commands work while they
#  move. The LCD shows both current angles all the time.
# =============================================================================
def paper_2024():
    import sys
    import select

    servo_x = PWM(Pin(20), freq=50)
    servo_y = PWM(Pin(21), freq=50)

    def set_angle(servo, angle):
        servo.duty_u16(int(1802 + angle / 180 * (7864 - 1802)))

    x, y = 90, 90                    # where the servos are now
    target_x, target_y = 90, 90      # where they're going
    command = ''

    # poll lets us check if a key was typed WITHOUT waiting for one
    keyboard = select.poll()
    keyboard.register(sys.stdin, select.POLLIN)

    while True:
        # 1. Read any typed characters
        while keyboard.poll(0):
            ch = sys.stdin.read(1)
            if ch == ';':
                # command is now something like 'X100'
                axis = command[:1]
                digits = command[1:]
                if axis in ('X', 'Y') and 1 <= len(digits) <= 3 \
                        and digits.isdigit() and int(digits) <= 180:
                    if axis == 'X':
                        target_x = int(digits)
                    else:
                        target_y = int(digits)
                command = ''
            elif ch in 'XY':
                command = ch             # start a new command
            elif ch.isdigit():
                command = command + ch

        # 2. Move each servo one degree toward its target
        if x < target_x:
            x += 1
        elif x > target_x:
            x -= 1
        if y < target_y:
            y += 1
        elif y > target_y:
            y -= 1
        set_angle(servo_x, x)
        set_angle(servo_y, y)

        # 3. Show the current angles
        show(0, 'X: ' + str(x))
        show(1, 'Y: ' + str(y))

        time.sleep_ms(15)                # sets the servo speed


if PAPER == 2022:
    paper_2022()
elif PAPER == 2023:
    paper_2023()
else:
    paper_2024()
