# =============================================================================
#  WEEK 10 - I2C AND THE LCD DISPLAY
#  Week 10 lecture + Lab 10.   Runs on: PICO WH (the subscriber Pico)
#  Needs lcd1602.py and umqtt on the Pico.
# =============================================================================
#  LAB 10 TASK
#  The subscriber shows the temperature on the LCD as a scrolling message:
#     "The temperature is 23 degrees. This is just right."
#     below 16 = too cold,  above 25 = too hot,  16 to 25 = just right
#  While the message scrolls (~5 seconds), IGNORE any new MQTT messages.
#  When it finishes, listen again and show the next reading.
#
#  LECTURE NOTES - I2C
#  * A slow, simple, low-power bus for small messages.
#  * 4 wires:  VCC (red), GND (black), SDA = data (white), SCL = clock (yellow)
#  * Many devices on one bus. Each has a 7-bit ADDRESS. The LCD is 0x3E.
#  * The Pico is the CONTROLLER, the LCD is the TARGET.
#  * A message: START, address + read/write bit, ACK, data bytes
#    (each ACKed), STOP.
#  * Command + data pattern: the first byte says what the rest means.
#    For the LCD:  0x80 = "next byte is a command"
#                  0x40 = "next byte is a character to show"
#  * LCD commands: HOME, DISPLAYON, CURSORON, BLINKON, DISPLAYOFF, CLEAR,
#    and 0b1RCCCCCC = move cursor to row R, column C.
#
#  LECTURE CODE (for reference)
#     i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100_000)
#     print([hex(a) for a in i2c.scan()])      # find devices -> ['0x3e']
#     i2c.writeto(ADDRESS, b'Hello')           # send bytes to a device
#     data = i2c.readfrom(ADDRESS, 12)         # read 12 bytes from a device
#
#  Sending to the LCD by hand (what lcd1602.py does for you):
#     i2c.writeto_mem(0x3E, 0x80, bytes([0x01]))      # command: clear
#     i2c.writeto_mem(0x3E, 0x40, bytes([ord('A')]))  # show the letter A
# =============================================================================

import network
import time
from machine import Pin, I2C
from umqtt.simple import MQTTClient
from lcd1602 import LCD1602

SSID = 'your-hotspot-name'
PASSWORD = 'your-hotspot-password'
BROKER = '192.168.43.10'
TOPIC = b'temp/pico'

i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100_000)
lcd = LCD1602(i2c, 2, 0)            # 2 rows, normal font

scrolling = False                   # True while a message is scrolling
new_temp = None                     # the latest temperature received


# Runs every time an MQTT message arrives
def on_message(topic, message):
    global new_temp
    if scrolling:
        print('Ignored a message while scrolling')
        return
    new_temp = float(message.decode())
    # (Using week 9 protobufs instead? Use:
    #  new_temp = temperature_upb2.TemperatureReading.decode(message).temperature)


def make_message(temp):
    temp = round(temp)
    if temp < 16:
        feeling = 'too cold'
    elif temp > 25:
        feeling = 'too hot'
    else:
        feeling = 'just right'
    return 'The temperature is ' + str(temp) + ' degrees. This is ' + feeling + '.'


def scroll(text):
    # The screen is 16 characters wide. Add 16 spaces before and after,
    # then show 16 characters at a time, moving one place each step.
    text = ' ' * 16 + text + ' ' * 16
    steps = len(text) - 16
    for i in range(steps + 1):
        lcd.setCursor(0, 0)
        lcd.print(text[i:i + 16])
        time.sleep(5 / steps)       # whole scroll takes about 5 seconds


# ---- Connect to WiFi ----
lcd.print('Connecting...')
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)
while wifi.status() != 3:
    time.sleep(1)

# ---- Connect to MQTT ----
mqtt = MQTTClient(client_id=b'lcd-subscriber', server=BROKER.encode(),
                  port=1883, keepalive=7000)
mqtt.set_callback(on_message)
mqtt.connect()
mqtt.subscribe(TOPIC)
lcd.clear()
lcd.print('Waiting...')

while True:
    # 1. Wait for a temperature
    new_temp = None
    while new_temp is None:
        mqtt.wait_msg()

    # 2. Scroll it, ignoring messages
    scrolling = True
    scroll(make_message(new_temp))

    # 3. Messages that arrived during the scroll are waiting in the queue.
    #    Read them now while scrolling is still True, so they're ignored.
    #    check_msg() doesn't wait, so this finishes quickly.
    for i in range(20):
        mqtt.check_msg()

    # 4. Start listening again
    scrolling = False
