# Lab 9 - MQTT + Protocol Buffers (Pico WH)
# Same file for publisher and subscriber: just change ROLE.

import network
import time
import ntptime
from machine import ADC
from umqtt.simple import MQTTClient
from temperature_upb2 import ReadingMessage, TimeMessage

# ---- settings ----
ROLE = "publisher"          # "publisher" or "subscriber"
PUBLISHER_ID = 1            # give each publisher Pico a different number
WIFI_SSID = "Danish"
WIFI_PASSWORD = "45894589"
BROKER = "127.0.1.1"     # IP address of the Pi 5 running mosquitto
TOPIC = b"temp/readings"


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        print("Connecting to WiFi...")
        time.sleep(1)
    print("WiFi connected:", wlan.ifconfig()[0])


def read_temperature():
    sensor = ADC(4)                      # Pico's built-in temperature sensor
    voltage = sensor.read_u16() * 3.3 / 65535
    return 27 - (voltage - 0.706) / 0.001721


def make_message():
    now = time.localtime()               # (year, month, day, hour, min, sec, ...)

    t = TimeMessage()
    t.hour = now[3]
    t.minute = now[4]
    t.second = now[5]

    reading = ReadingMessage()
    reading.publisher_id = PUBLISHER_ID
    reading.temperature = read_temperature()
    reading.time = t.serialize()         # nested message is set as bytes
    return reading.serialize()


def on_message(topic, data):
    reading = ReadingMessage()
    reading.parse(data)
    t = reading.time.value()
    print("Publisher {} | {:.2f} C | {:02d}:{:02d}:{:02d}".format(
        reading.publisher_id.value(),
        reading.temperature.value(),
        t.hour.value(), t.minute.value(), t.second.value()))


# ---- main program ----
connect_wifi()
ntptime.settime()                        # set the Pico clock from the internet (UTC)

client = MQTTClient("pico-" + str(PUBLISHER_ID) + "-" + ROLE, BROKER)
client.connect()
print("Connected to broker as", ROLE)

if ROLE == "publisher":
    while True:
        data = make_message()
        client.publish(TOPIC, data)
        print("Sent", len(data), "bytes")
        time.sleep(5)
else:
    client.set_callback(on_message)
    client.subscribe(TOPIC)
    while True:
        client.wait_msg()                # blocks until a message arrives