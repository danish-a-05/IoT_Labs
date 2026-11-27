# =============================================================================
#  WEEK 3 - WIFI, SOCKETS AND A SIMPLE HTTP SERVER
#  Week 3 lecture + Lab 3.   Runs on: PICO WH
# =============================================================================
#  LAB 3 TASK
#  Open  http://<pico-ip>/led?brightness=0.2  in a browser -> LED at 20%.
#  Anything invalid -> reply 404 with an error message, and DON'T crash:
#    * wrong path   * brightness not a number   * brightness not in 0..1
#  Scale 0..1 to 0..55000 (not the full 65535) to protect the LED.
#
#  LECTURE NOTES
#  * OSI model: data passes down through layers, each adds its own header.
#  * Addresses: WiFi/Ethernet = MAC address, IP = IP address, TCP = port.
#  * Typing google.ie: DNS lookup -> HTTP request -> TCP segment ->
#    IP packet -> WiFi frame -> sent.
#  * The Pico only supports 2.4GHz WiFi. Set your hotspot to 2.4GHz.
#  * Sockets send and receive BYTES, not strings:
#       bytes -> str:  b'abc'.decode()       str -> bytes: 'abc'.encode()
#  * Useful string methods: [x:y] slicing, .startswith(), .find(), .split()
#
#  LECTURE CODE (for reference)
#  ---- Scan for networks ----
#     for (ssid, bssid, channel, rssi, security, hidden) in wifi.scan():
#         print(ssid.decode(), channel)
#  ---- DNS lookup ----
#     ip = socket.getaddrinfo('tudublin.ie', 443)[0][-1][0]
# =============================================================================

import network
import socket
import time
from machine import Pin, PWM

SSID = 'your-hotspot-name'
PASSWORD = 'your-hotspot-password'

led = PWM(Pin(16), freq=1000)


# Lecture function: returns True once connected (status 3 = got an IP)
def connect(wifi, ssid, password, timeout=10):
    wifi.connect(ssid, password)
    while timeout > 0:
        if wifi.status() == 3:
            return True
        time.sleep(1)
        timeout -= 1
    return False


# Returns the brightness as a number, or None if the request is invalid
def get_brightness(path):
    if not path.startswith('/led?brightness='):
        return None                          # wrong path

    text = path[len('/led?brightness='):]    # the part after the '='
    try:
        value = float(text)
    except ValueError:
        return None                          # not a number

    if value < 0 or value > 1:
        return None                          # out of range
    return value


wifi = network.WLAN(network.STA_IF)
wifi.active(True)

if not connect(wifi, SSID, PASSWORD):
    print("Wifi couldn't connect")
else:
    s = socket.socket()
    s.bind(('0.0.0.0', 80))                  # port 80 = normal web port
    s.listen()
    print('Open http://' + wifi.ifconfig()[0] + '/led?brightness=0.5')

    while True:
        cxn, addr = s.accept()               # wait for a browser to connect
        try:
            request = cxn.recv(1024).decode()
            # First line looks like:  GET /led?brightness=0.2 HTTP/1.1
            first_line = request.split('\r\n')[0]
            method, path, version = first_line.split(' ')

            brightness = get_brightness(path)

            if method != 'GET' or brightness is None:
                cxn.send(b'HTTP/1.1 404 Not Found\r\n\r\n')
                cxn.send(b'Error: use /led?brightness=<number from 0 to 1>')
            else:
                led.duty_u16(int(brightness * 55000))
                cxn.send(b'HTTP/1.1 200 OK\r\n\r\n')
                cxn.send(b'Brightness set to ' + str(brightness).encode())
        except Exception as e:
            # Garbage that isn't even a proper HTTP request: still reply
            # 404, print the error, and keep running (never crash).
            print('Bad request:', e)
            cxn.send(b'HTTP/1.1 404 Not Found\r\n\r\nBad request')
        cxn.close()
