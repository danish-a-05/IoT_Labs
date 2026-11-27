# =============================================================================
#  WEEK 5 - SECURITY AND AES ENCRYPTION
#  Week 5 lecture + Lab 5.   Runs on: PICO WH  (laptop server at the bottom)
# =============================================================================
#  LAB 5 TASK
#  * Read the temperature every 2 seconds using a Timer.
#  * Encrypt it with AES and send it to a server on your laptop.
#  * The LED web server from lab 3 must keep working at the same time.
#  * The laptop decrypts the readings and prints them.
#
#  LECTURE NOTES
#  Real IoT hacks: Ring cameras, St. Jude heart devices, Mirai botnet.
#  Common problems and fixes:
#    * Default passwords     -> force a change on first login, use 2FA
#    * One level of access   -> separate normal users and admins
#    * Big attack surface    -> close ports you don't need, no full OS
#    * Old software          -> keep it updated; never write your own crypto
#    * No encryption         -> encrypt anything that could be sensitive
#    * Trusted computing     -> check firmware isn't tampered (Secure Boot/DICE)
#    * Bad vendor response   -> have a plan, tell customers, push updates
#  Three types of encryption:
#    * Symmetric  - ONE shared key encrypts and decrypts (AES, Blowfish)
#    * Asymmetric - public key encrypts, private key decrypts (RSA)
#    * Hashing    - one-way, can't be reversed, for passwords (SHA-2, SHA-3)
#  RSA (slides 14-15):
#    n = p*q,  λ = lcm(p-1, q-1),  pick e with gcd(e, λ) = 1,
#    pick d with (e*d) % λ == 1      (the slide says % n - that's a typo)
#    encrypt: c = pow(m, e, n)       decrypt: m = pow(c, d, n)
#  AES works on 16-byte blocks. Modes:
#    * ECB - each block encrypted separately. BAD: patterns leak.
#    * CBC - each block is mixed with the previous one, the first with an
#            IV (initialisation vector). This is what we use. Mode number 2.
#
#  AES RULES IN MICROPYTHON (cryptolib)
#    * key must be 16 bytes, IV 16 bytes, data a multiple of 16 bytes
#    * a cipher object can encrypt OR decrypt, not both -> make a new one
#
#  HOW THIS PROGRAM WORKS
#  The Timer calls send_temperature() every 2 seconds, in the background.
#  Meanwhile the main loop runs the normal LED web server. We send with UDP
#  because it needs no connection: just sendto(data, address).
# =============================================================================

import network
import socket
import time
import cryptolib
from machine import Pin, PWM, ADC, Timer

SSID = 'your-hotspot-name'
PASSWORD = 'your-hotspot-password'
LAPTOP_IP = '192.168.43.50'          # your laptop's IP address
LAPTOP_PORT = 5005

KEY = b'sixteen byte key'            # exactly 16 bytes, same on the laptop
IV = b'sixteen byte iv!'             # exactly 16 bytes, same on the laptop
# (A fixed IV, like in the lecture, is fine for the lab. In real life use a
#  new random IV each time, so the same temperature doesn't always encrypt
#  to the same bytes.)

led = PWM(Pin(16), freq=1000)
temp_sensor = ADC(4)                 # the built-in thermometer is ADC 4
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # UDP socket


# Code from the lab sheet
def read_temp():
    value = temp_sensor.read_u16()
    voltage = value * (3.3 / 2 ** 16)
    return 27 - (voltage - 0.706) / 0.001721


def send_temperature(t):
    text = '{:.2f}'.format(read_temp())     # e.g. '23.47'

    # AES needs 16 bytes: pad with spaces. The laptop strips them off.
    text = text + ' ' * (16 - len(text))

    cipher = cryptolib.aes(KEY, 2, IV)      # 2 = CBC mode
    encrypted = cipher.encrypt(text.encode())

    udp.sendto(encrypted, (LAPTOP_IP, LAPTOP_PORT))
    print('sent', text.strip())


# ---- Connect to WiFi ----
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)
while wifi.status() != 3:
    print('connecting...')
    time.sleep(1)
print('Pico IP:', wifi.ifconfig()[0])

# ---- Every 2000 ms, call send_temperature ----
timer = Timer()
timer.init(period=2000, mode=Timer.PERIODIC, callback=send_temperature)

# ---- LED web server from lab 3 keeps running ----
s = socket.socket()
s.bind(('0.0.0.0', 80))
s.listen()

while True:
    cxn, addr = s.accept()
    try:
        path = cxn.recv(1024).decode().split(' ')[1]
        brightness = float(path.split('=')[1])
        if path.startswith('/led?brightness=') and 0 <= brightness <= 1:
            led.duty_u16(int(brightness * 55000))
            cxn.send(b'HTTP/1.1 200 OK\r\n\r\nOK')
        else:
            cxn.send(b'HTTP/1.1 404 Not Found\r\n\r\nInvalid')
    except Exception:
        cxn.send(b'HTTP/1.1 404 Not Found\r\n\r\nInvalid')
    cxn.close()


# =============================================================================
#  LAPTOP SERVER - save this part as server.py on your laptop
#  (pip install pycryptodome), then run:  python server.py
# =============================================================================
# import socket
# from Crypto.Cipher import AES
#
# KEY = b'sixteen byte key'          # must match the Pico
# IV = b'sixteen byte iv!'
#
# udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# udp.bind(('0.0.0.0', 5005))
# print('Waiting for temperatures...')
#
# while True:
#     encrypted, addr = udp.recvfrom(1024)
#     cipher = AES.new(KEY, AES.MODE_CBC, IV)   # new cipher every time
#     text = cipher.decrypt(encrypted).decode().strip()
#     print('Temperature from', addr[0], ':', text, 'C')
#
# (If nothing arrives, allow Python through the laptop's firewall.)
#
# LECTURE AES EXAMPLE (for reference):
#     cipher = cryptolib.aes(padded_key, 2, padded_iv)
#     ciphertext = cipher.encrypt(padded_data)
#     cipher = cryptolib.aes(padded_key, 2, padded_iv)   # new object!
#     plaintext = cipher.decrypt(ciphertext)
