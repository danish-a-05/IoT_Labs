# =============================================================================
#  WEEK 8 - RASPBERRY PI + MQTT
#  Week 8 lecture + Lab 8.   Runs on: PICO WH (both Picos use this file)
# =============================================================================
#  LAB 8 SYSTEM
#    Pico 1 (publisher)  --temp/pico-->  Raspberry Pi (Mosquitto broker)
#    Pico 2 (subscriber) <--temp/pico--  Raspberry Pi
#  The subscriber turns on an LED (or the fan) when temp is 25 or more.
#  Set ROLE below to 'publisher' on one Pico and 'subscriber' on the other.
#
#  LECTURE NOTES
#  * Raspberry Pi = a full computer running Linux.
#    Pico = a microcontroller with no operating system.
#  * Pi 5: 2.4GHz 4-core ARM CPU, 4-16GB RAM, WiFi, Ethernet, no built-in
#    storage (boots from an SD card).
#  * Pi pin numbers: BCM (GPIO17) vs BOARD (physical pin 11).
#    gpiozero uses BCM numbers.
#  * Motor controller: a GPIO pin can't supply enough current to run a
#    motor, so a motor controller switches a separate power supply for it.
#    The servo has one built in.
#  * MQTT words: broker = central server, topic = channel,
#    publisher = sends messages, subscriber = receives them.
#    Topics are created automatically the first time they're used.
#
#  LECTURE CODE - gpiozero on the Raspberry Pi (for reference)
#     import gpiozero
#     led = gpiozero.LED(17);       led.on();  led.off();  led.toggle()
#     led = gpiozero.PWMLED(12);    led.value = 0.5          # 0.0 to 1.0
#     button = gpiozero.Button(17); button.wait_for_press()
#     button.when_pressed = my_function    # no brackets: it's called later
#
#  RASPBERRY PI SETUP (type in the Pi's terminal)
#     sudo apt update && sudo apt dist-upgrade -y
#     sudo apt install mosquitto mosquitto-clients
#     Test it in two terminals:
#        mosquitto_sub -h localhost -t temp/pico
#        mosquitto_pub -h localhost -t temp/pico -m "20"
#     Allow other devices to connect - edit the config with
#     sudo nano /etc/mosquitto/mosquitto.conf  so it contains:
#        listener 1883
#        socket_domain ipv4
#        protocol mqtt
#        allow_anonymous true
#     Then:  sudo systemctl restart mosquitto
#     Find the Pi's IP address with:  hostname -I
#
#  ON EACH PICO, install the MQTT library once (with WiFi connected):
#     import mip
#     mip.install('umqtt.simple')
#     mip.install('umqtt.robust')
# =============================================================================

import network
import time
import machine
from machine import Pin, ADC
from umqtt.simple import MQTTClient

ROLE = 'publisher'                  # 'publisher' or 'subscriber'
SSID = 'your-hotspot-name'
PASSWORD = 'your-hotspot-password'
BROKER = '192.168.43.10'            # the Raspberry Pi's IP address
TOPIC = b'temp/pico'


def read_temp():
    voltage = ADC(4).read_u16() * (3.3 / 2 ** 16)
    return 27 - (voltage - 0.706) / 0.001721


# Runs every time a message arrives (subscriber only)
def on_message(topic, message):
    temp = float(message.decode())       # message is bytes, e.g. b'26.10'
    print('Received', temp)
    if temp >= 25:
        output.value(1)                  # turn LED / fan on
    else:
        output.value(0)                  # turn it off


# ---- Connect to WiFi ----
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)
while wifi.status() != 3:
    print('connecting...')
    time.sleep(1)

# ---- Connect to the broker ----
# Each Pico needs a DIFFERENT client_id, otherwise the broker keeps
# disconnecting one of them. Using the role name is enough.
mqtt = MQTTClient(client_id=ROLE.encode(), server=BROKER.encode(),
                  port=1883, keepalive=7000)

if ROLE == 'publisher':
    mqtt.connect()
    while True:
        temp = read_temp()
        mqtt.publish(TOPIC, str(temp).encode())   # MQTT sends bytes
        print('Sent', temp)
        time.sleep(1)

else:
    output = Pin(16, Pin.OUT)          # LED, or the fan's motor controller
    mqtt.set_callback(on_message)      # set this BEFORE subscribing
    mqtt.connect()
    mqtt.subscribe(TOPIC)              # the lab template forgets this line!
    while True:
        mqtt.wait_msg()                # wait for a message, then on_message
                                       # runs. check_msg() = don't wait.
