# =============================================================================
#  WEEK 9 - ADVANCED ARCHITECTURES + PROTOCOL BUFFERS OVER MQTT
#  Week 9 lecture + Lab 9.   Runs on: PICO WH (both Picos use this file)
# =============================================================================
#  LAB 9 TASK
#  Same system as week 8, but send each reading as a protocol buffer
#  containing the temperature, the publisher's ID and the time.
#
#  LECTURE NOTES
#  * Three architectures: device-to-cloud, device-to-gateway, device-to-device
#  * Three tiers of an IoT system:
#       Tier 1 - edge devices    (our Picos)
#       Tier 2 - gateway         (our Raspberry Pi)
#       Tier 3 - cloud
#  * Alexa skills: speech -> text -> matched to an INTENT. Your handler
#    class extends AbstractRequestHandler and overrides
#    can_handle() (can I handle this?) and handle() (build the reply).
#  * Protocol buffers (Google, 2001): you write a SCHEMA, and the protoc
#    compiler generates code that turns messages into small binary data.
#    Smaller than JSON because only field NUMBERS are sent, not names.
#  * gRPC: Google's remote procedure calls, built on protobuf.
#
#  STEP 1 - save this as temperature.proto
#  (uprotobuf only supports proto VERSION 2)
#
#     syntax = "proto2";
#
#     message Time {
#       optional int32 hour = 1;
#       optional int32 minute = 2;
#       optional int32 second = 3;
#     }
#
#     message TemperatureReading {
#       optional float temperature = 1;
#       optional string publisher_id = 2;
#       optional Time time = 3;
#     }
#
#  Use "optional", not "required": uprotobuf doesn't send a field that
#  is 0, and with "required" that would be an error on the other side.
#
#  STEP 2 - compile it (on the Raspberry Pi or laptop)
#     sudo apt install protobuf-compiler
#     git clone https://github.com/T0ha/uprotobuf
#     protoc --plugin=protoc-gen-custom=uprotobuf/scripts/uprotobuf_plugin.py --custom_out=. temperature.proto
#  This makes temperature_upb2.py. Copy it AND uprotobuf/protobuf/uprotobuf.py
#  to the Pico.
#  (For normal Python on a laptop:  protoc --python_out=. temperature.proto
#   makes temperature_pb2.py; there you use SerializeToString() and
#   ParseFromString(data) instead of encode() and decode().)
#
#  STEP 3 - the code below.
#    msg.encode()                          -> bytes to send
#    TemperatureReading.decode(data)       -> RETURNS a new message object
# =============================================================================

import network
import time
import machine
from machine import Pin, ADC
from umqtt.simple import MQTTClient
import temperature_upb2

ROLE = 'publisher'                  # 'publisher' or 'subscriber'
SSID = 'your-hotspot-name'
PASSWORD = 'your-hotspot-password'
BROKER = '192.168.43.10'            # the Raspberry Pi's IP address
TOPIC = b'temp/pico'


def read_temp():
    voltage = ADC(4).read_u16() * (3.3 / 2 ** 16)
    return 27 - (voltage - 0.706) / 0.001721


# Runs every time a message arrives (subscriber only)
def on_message(topic, data):
    msg = temperature_upb2.TemperatureReading.decode(data)
    print(msg.publisher_id, msg.time.hour, msg.time.minute,
          msg.time.second, msg.temperature)
    if msg.temperature >= 25:
        output.value(1)
    else:
        output.value(0)


# ---- Connect to WiFi ----
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)
while wifi.status() != 3:
    print('connecting...')
    time.sleep(1)

mqtt = MQTTClient(client_id=ROLE.encode(), server=BROKER.encode(),
                  port=1883, keepalive=7000)

if ROLE == 'publisher':
    # The Pico's clock starts wrong at power-on. ntptime sets it from the
    # internet (UTC time, which is Irish time in winter).
    import ntptime
    ntptime.settime()

    mqtt.connect()
    while True:
        now = time.localtime()   # (year, month, day, hour, min, sec, ...)

        msg = temperature_upb2.TemperatureReading()
        msg.temperature = read_temp()
        msg.publisher_id = 'pico-1'
        msg.time.hour = now[3]
        msg.time.minute = now[4]
        msg.time.second = now[5]

        mqtt.publish(TOPIC, msg.encode())     # encode() gives bytes
        print('Sent', msg.temperature)
        time.sleep(1)

else:
    output = Pin(16, Pin.OUT)
    mqtt.set_callback(on_message)
    mqtt.connect()
    mqtt.subscribe(TOPIC)
    while True:
        mqtt.wait_msg()
