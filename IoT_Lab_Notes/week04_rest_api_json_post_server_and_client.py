# =============================================================================
#  WEEK 4 - SYSTEM ARCHITECTURES, REST AND JSON
#  Week 4 lecture + Lab 4.   Runs on: PICO WH  (laptop client at the bottom)
# =============================================================================
#  LAB 4 TASK
#  Add a route  POST /rest/led  whose body is JSON:
#        {"brightness": 0.3, "request": true}
#  * "brightness" and "request" must both be there (other keys ignored).
#  * If "request" is false -> ignore it.
#  * Otherwise set the LED and reply with ONLY:
#        {"brightness": 0.3, "request": false}
#  * A browser can't easily send this, so write a client for the laptop.
#
#  LECTURE NOTES
#  Three IoT architectures (learn these!):
#    1. Device-to-cloud   - device talks straight to a cloud server
#    2. Device-to-gateway - device talks to a local hub, hub talks to cloud
#    3. Device-to-device  - devices talk to each other (e.g. mesh network)
#  Don't invent your own protocol - it will be less secure and less tested.
#  REST:
#    * client-server, STATELESS (server doesn't remember you between requests)
#    * usually JSON inside HTTP
#    * stateless -> easy to cache and load-balance
#    * GET = read data, POST = send data / do an action
#  MQTT (used in week 8): publish/subscribe through a central BROKER.
#    Topic = channel, publisher = sender, subscriber = receiver.
#  Cloud computing: processing on central servers.
#    Problems: security, privacy, GDPR, vendor lock-in.
#  Fog/edge computing: processing done on/near the devices.
#    Problems: dearer devices, more power, firmware updates, more e-waste.
# =============================================================================

import network
import socket
import json
import time
from machine import Pin, PWM

SSID = 'your-hotspot-name'
PASSWORD = 'your-hotspot-password'

led = PWM(Pin(16), freq=1000)

# ---- Connect to WiFi ----
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)
while wifi.status() != 3:
    print('connecting...')
    time.sleep(1)

# ---- Start the server ----
s = socket.socket()
s.bind(('0.0.0.0', 80))
s.listen()
print('Send POST requests to http://' + wifi.ifconfig()[0] + '/rest/led')

while True:
    cxn, addr = s.accept()
    try:
        request = cxn.recv(1024).decode()

        # An HTTP request is: headers, then a blank line, then the body.
        # Splitting on the blank line separates them. Headers we don't
        # need are simply never looked at.
        headers, body = request.split('\r\n\r\n', 1)

        first_line = headers.split('\r\n')[0]   # POST /rest/led HTTP/1.1
        method, path, version = first_line.split(' ')

        if method == 'POST' and path == '/rest/led':
            if body == '':
                # Some clients send the body in a second packet
                body = cxn.recv(1024).decode()
            data = json.loads(body)             # JSON text -> dictionary

            if 'brightness' in data and 'request' in data:
                if data['request'] == True:
                    brightness = data['brightness']
                    led.duty_u16(int(brightness * 55000))
                    reply = {'brightness': brightness, 'request': False}
                    cxn.send(b'HTTP/1.1 200 OK\r\n')
                    cxn.send(b'Content-Type: application/json\r\n\r\n')
                    cxn.send(json.dumps(reply).encode())
                else:
                    # request was false -> ignore it
                    cxn.send(b'HTTP/1.1 200 OK\r\n\r\n')
            else:
                cxn.send(b'HTTP/1.1 400 Bad Request\r\n\r\nMissing keys')
        else:
            cxn.send(b'HTTP/1.1 404 Not Found\r\n\r\n')
    except Exception as e:
        print('Bad request:', e)
        cxn.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')
    cxn.close()


# =============================================================================
#  LAPTOP CLIENT - save this part as client.py on your laptop
#  (pip install requests), then run:  python client.py
# =============================================================================
# import requests
#
# PICO_IP = '192.168.43.100'          # the IP the Pico printed
#
# while True:
#     brightness = float(input('Brightness 0-1: '))
#     message = {'brightness': brightness, 'request': True}
#     # json= turns the dictionary into JSON and sets Content-Type for you
#     r = requests.post('http://' + PICO_IP + '/rest/led', json=message)
#     print(r.status_code, r.text)
#
# NOTE: urequests is MicroPython's version of requests. You would only
# need it if the Pico itself were the client.
