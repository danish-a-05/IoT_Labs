# =============================================================================
#  WEEK 1 - INTRODUCTION TO IoT AND BASIC ELECTRONICS
#  Lecture 1 + Lab 1.   Runs on: LAPTOP
# =============================================================================
#  Lab 1 used the Falstad circuit simulator (falstad.com/circuit), so there
#  is no Pico code this week. This file turns the electronics rules into
#  small functions you can use to check answers.
#
#  LECTURE NOTES
#  IoT = putting cheap computers in everyday things and connecting them to
#  the internet (smart speakers, smart lights, road signs, farming).
#  Downsides: security, privacy, vendor lock-in, cost, e-waste.
#  Different from normal CS: limited resources, close to the hardware,
#  unusual inputs/outputs (sensors, motors, LEDs).
#
#  Voltage (V, volts)  = electrical "pressure"
#  Current (I, amps)   = electrical "flow"
#  Ohm's law:  V = I * R
#
#  Resistor    (ohms)    - slows current down
#  Capacitor   (farads)  - stores a little charge, like a tiny battery
#  Inductor    (henries) - stores energy in a magnetic field
#  Diode                 - current flows one way only (LED = light diode)
#  Transformer           - changes voltage
#  Transistor            - a switch: ON when the base voltage is high enough
#
#  LAB 1 NOTES
#  * RLC circuit: energy bounces between the capacitor and the inductor,
#    getting weaker each time because the resistor wastes some.
#  * Current takes the path of least resistance: a closed switch with no
#    resistor bypasses the resistors next to it.
#  * Transistor: flip the base switch on and current flows through it.
# =============================================================================


def series_resistance(r1, r2):
    # Resistors in a line: add them up
    return r1 + r2


def parallel_resistance(r1, r2):
    # Resistors side by side: 1/R = 1/R1 + 1/R2
    return 1 / (1 / r1 + 1 / r2)


def parallel_capacitance(c1, c2):
    # Capacitors are the opposite of resistors: in parallel they add up
    return c1 + c2


def series_capacitance(c1, c2):
    # ...and in series they use the 1/C rule
    return 1 / (1 / c1 + 1 / c2)


def voltage_divider(v_in, r1, r2):
    # Two resistors in series. Voltage at the point between them:
    # Vout = Vin * R2 / (R1 + R2)   (R2 is the one connected to ground)
    # A potentiometer is a voltage divider you can adjust by turning it.
    return v_in * r2 / (r1 + r2)


print('Current through 220 ohms at 5V:', 5 / 220, 'A')
print('100 + 200 ohms in series:', series_resistance(100, 200))
print('100 and 100 ohms in parallel:', parallel_resistance(100, 100))
print('10uF and 22uF in parallel:', parallel_capacitance(10, 22), 'uF')
print('10uF and 10uF in series:', series_capacitance(10, 10), 'uF')
print('Divider 3.3V, 5k, 5k:', voltage_divider(3.3, 5000, 5000), 'V')
