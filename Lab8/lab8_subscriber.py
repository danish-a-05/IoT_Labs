# Lab 8 - MQTT with the Raspberry Pi
# SUBSCRIBER Pico WH: receives temperatures on temp/pico and turns on an
# LED (or fan) when the temperature is 25 degrees C or more
# Team: <Name 1 (student no.)>, <Name 2 (student no.)>, <Name 3 (student no.)>

import network
import time
import machine
import umqtt.robust as umqtt

# --- Settings: change these to match your setup ---
SSID = 'Danish'
PASSWORD = '45894589'
HOSTNAME = '10.78.157.146' # Raspberry Pi IP address (run `hostname -I` on the Pi)
PORT = 8080
TOPIC = b'temp/pico'
CLIENT_ID = b'pico_subscriber' # must be different from the publisher's ID
THRESHOLD = 25.0 # degrees C

# --- Outputs ---
# output_pin drives an external LED (via a resistor) or the fan's motor
# controller input. Change 15 to whichever GPIO pin you wired it to.
# The onboard LED copies it so you can see it working without wiring.
output_pin = machine.Pin(15, machine.Pin.OUT)
onboard_led = machine.Pin('LED', machine.Pin.OUT)

# --- Connect to Wi-Fi (same as the publisher) ---
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    for _ in range(20):
        if wlan.isconnected():
            break
        print('Connecting to Wi-Fi...')
        time.sleep(1)
    if not wlan.isconnected():
        raise RuntimeError('Could not connect to Wi-Fi')
    print('Wi-Fi connected, Pico IP:', wlan.ifconfig()[0])
    

# --- Callback: runs every time a message arrives ---
# topic and message both arrive as bytes.
# 1. Ignore anything that is not on temp/pico (the TODO in the template).
# 2. Convert the message to a float; skip it if it isn't a number.
# 3. Turn the output on at or above the threshold, off below it.
def callback(topic, message):
    if topic != TOPIC:
        return
    try:
        temp = float(message.decode())
    except ValueError:
        print('Ignoring non-numeric message:', message)
        return
    if temp >= THRESHOLD:
        output_pin.value(1)
        onboard_led.value(1)
        print('Received', temp, 'C -> ON (at or above', THRESHOLD, ')')
    else:
        output_pin.value(0)
        onboard_led.value(0)
        print('Received', temp, 'C -> OFF')
        
        
# --- Connect to the broker and subscribe ---
# set_callback must be called BEFORE subscribe, otherwise early
# messages have nowhere to go.
def connect_mqtt():
        client = umqtt.MQTTClient(
        client_id=CLIENT_ID,
        server=HOSTNAME.encode(),
        port=PORT,
        keepalive=7000
    )
    client.set_callback(callback)
    client.connect()
    client.subscribe(TOPIC)
    print('Connected to', HOSTNAME, 'and subscribed to', TOPIC.decode())
    return client


# --- Main loop ---
# Start with the output off, then wait for messages forever.
# wait_msg() blocks until a message arrives, then calls callback().
# umqtt.robust reconnects automatically if the connection drops.
output_pin.value(0)
onboard_led.value(0)
connect_wifi()
mqtt = connect_mqtt()

while True:
    mqtt.wait_msg()