# =============================================================================
#  WEEK 2 - PICO WH: LED, PWM, POTENTIOMETER, SERVO
#  Lecture 2 + Lab 2.   Runs on: PICO WH
# =============================================================================
#  LAB 2 TASK: turn a potentiometer to control BOTH the brightness of an LED
#  and the angle of a servo.
#
#  LECTURE NOTES
#  * Pico WH: RP2040 chip (2 cores, 133MHz), 256KB RAM, 2MB flash,
#    26 GPIO pins, I2C + SPI. "W" = WiFi, "H" = headers soldered on.
#  * MicroPython = Python for microcontrollers. Runs with NO operating system.
#  * Potentiometer = a knob. The Pico reads it with an ADC
#    (analogue-to-digital converter) as a number from 0 to 65535.
#  * PWM = switch a pin on/off very fast. duty_u16(0..65535) sets how much
#    of the time it is ON:
#       LED   -> more ON time = brighter        (use freq=1000)
#       servo -> length of the ON pulse = angle (use freq=50)
#
#  LECTURE CODE (for reference)
#  ---- Blink the on-board LED ----
#     led = machine.Pin('LED', machine.Pin.OUT)
#     while True:
#         led.value(1); time.sleep(1)
#         led.value(0); time.sleep(1)
#
#  ---- Blink with a Timer (doesn't block the program) ----
#     def tick(t):              # the callback MUST take one argument
#         led.toggle()          # (the slide forgot it -> TypeError)
#     timer = Timer()
#     timer.init(freq=0.5, mode=Timer.PERIODIC, callback=tick)
#
#  ---- RGB LED (needs ws2812.py on the Pico) ----
#     from ws2812 import WS2812
#     led = WS2812(18, 1)                  # pin 18, 1 LED
#     led.pixels_set(0, (255, 0, 0))       # red
#     led.pixels_show()
#
#  ---- Read a potentiometer ----
#     adc = ADC(1)
#     print(adc.read_u16())                # 0 .. 65535
# =============================================================================

from machine import Pin, PWM, ADC
import time

# Change these to match where you plugged things in
pot = ADC(0)                       # ADC(0) = GP26
led = PWM(Pin(16), freq=1000)      # LED on GP16
servo = PWM(Pin(20), freq=50)      # servo on GP20 (servos need 50Hz)


def move_servo(angle):
    # From the lecture: 1802 = 0 degrees, 7864 = 180 degrees
    duty = 1802 + (angle / 180) * (7864 - 1802)
    servo.duty_u16(int(duty))


while True:
    value = pot.read_u16()          # 0 .. 65535

    led.duty_u16(value)             # same range, so use it directly

    angle = value / 65535 * 180     # turn 0..65535 into 0..180
    move_servo(angle)

    print(value, int(angle))
    time.sleep(0.05)
