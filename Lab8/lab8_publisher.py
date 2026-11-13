# Lab 8 - MQTT with the Raspberry Pi
# PUBLISHER Pico WH: reads the temperature and publishes it to temp/pico
# Team: <Name 1 (student no.)>, <Name 2 (student no.)>, <Name 3 (student no.)>

import network
import time
import machine
import umqtt.robust as umqtt

# --- Settings: change these to match your setup ---
SSID = 'Danish'
PASSWORD = '45894589'
HOSTNAME = '10.78.157.146' # Raspberry Pi IP address (run `hostname -I` on the Pi)
PORT = 8080 # default MQTT port
TOPIC = b'temp/pico'
CLIENT_ID = b'pico_publisher' # must be different from the subscriber's ID
SEND_INTERVAL = 0.5 # seconds between readings (twice per second)

# --- Connect to Wi-Fi ---
# Turns on the Wi-Fi chip in station (client) mode and joins the hotspot.
# Gives up after 20 seconds so it doesn't hang forever.
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
    
    
# --- Read the temperature ---
# Uses the Pico's built-in temperature sensor on ADC channel 4.

# read_u16() gives 0-65535, converted to a voltage (0-3.3 V), then to
# degrees Celsius with the formula from the RP2040 datasheet.
sensor = machine.ADC(4)
CONVERSION_FACTOR = 3.3 / 65535

def read_temperature():
    voltage = sensor.read_u16() * CONVERSION_FACTOR
    return 27 - (voltage - 0.706) / 0.001721

# --- Connect to the MQTT broker on the Raspberry Pi ---
# keepalive: if the broker hears nothing for this many seconds it drops us.
def connect_mqtt():
    client = umqtt.MQTTClient(
        client_id=CLIENT_ID,
        server=HOSTNAME.encode(),
        port=PORT,
        keepalive=7000
    )
    client.connect()
    print('Connected to MQTT broker at', HOSTNAME)
    return client


# --- Main loop ---
# Read the temperature, round it to 2 decimal places, and publish it as text.
# MQTT messages are bytes, so the number is converted str -> bytes.
# umqtt.robust automatically reconnects if the connection drops.
connect_wifi()
mqtt = connect_mqtt()

while True:
    temp = round(read_temperature(), 2)
    mqtt.publish(TOPIC, str(temp).encode())
    print('Published', temp, 'to', TOPIC.decode())
    time.sleep(SEND_INTERVAL)
