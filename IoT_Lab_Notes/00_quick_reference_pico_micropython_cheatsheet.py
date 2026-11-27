# =============================================================================
#  00 - QUICK REFERENCE: PICO WH + MICROPYTHON
#  Every snippet you need, in one place. The week files have full examples.
# =============================================================================
#
#  FILES
#   week01 electronics (laptop)        week06 data analysis (laptop)
#   week02 LED, pot, servo             week08 MQTT publisher/subscriber
#   week03 WiFi + HTTP server          week09 protocol buffers + MQTT
#   week04 REST + JSON                 week10 I2C + LCD scrolling
#   week05 AES + timer                 labtest_practice (past papers)
#   lcd1602.py = LCD driver. Copy it to the Pico with this exact name.
#
#  THONNY
#   * Save to the PICO, not your computer. main.py runs at power-on.
#   * Ctrl+C stops a running program.
#   * Install libraries (Pico must be on WiFi):
#         import mip;  mip.install('umqtt.simple')
#
#  PINS
#   * Pin(15) means GP15, not physical pin 15.
#   * Analogue (ADC): GP26 = ADC(0), GP27 = ADC(1), GP28 = ADC(2).
#     ADC(4) = built-in thermometer.
#   * Any pin can do PWM.   I2C0: SDA = GP8, SCL = GP9.
#   * On-board LED: Pin('LED').    WiFi: 2.4GHz only.
# =============================================================================

from machine import Pin, PWM, ADC, Timer, I2C
import time

# ---- Output (LED) ----
led = Pin('LED', Pin.OUT)
led.value(1)                       # on
led.value(0)                       # off
led.toggle()

# ---- Input (button) ----
# button = Pin(16, Pin.IN, Pin.PULL_DOWN)
# button.value()                   # 1 when pressed (Grove button)

# ---- PWM ----
# dim = PWM(Pin(16), freq=1000)
# dim.duty_u16(32768)              # 0..65535 -> 50% brightness
# servo = PWM(Pin(20), freq=50)
# servo.duty_u16(1802)             # 0 degrees  (7864 = 180 degrees)

# ---- Potentiometer ----
# pot = ADC(0)
# pot.read_u16()                   # 0..65535

# ---- Temperature ----
def read_temp():
    voltage = ADC(4).read_u16() * (3.3 / 2 ** 16)
    return 27 - (voltage - 0.706) / 0.001721
# Fahrenheit = C * 9 / 5 + 32

# ---- Timer: run a function every 2 seconds ----
# def job(t):                      # must take one argument
#     print(read_temp())
# timer = Timer()
# timer.init(period=2000, mode=Timer.PERIODIC, callback=job)
# timer.deinit()                   # stop it

# ---- WiFi ----
# import network
# wifi = network.WLAN(network.STA_IF)
# wifi.active(True)
# wifi.connect('SSID', 'PASSWORD')
# while wifi.status() != 3: time.sleep(1)
# print(wifi.ifconfig()[0])        # the Pico's IP address

# ---- Web server ----
# import socket
# s = socket.socket(); s.bind(('0.0.0.0', 80)); s.listen()
# cxn, addr = s.accept()
# request = cxn.recv(1024).decode()
# cxn.send(b'HTTP/1.1 200 OK\r\n\r\nHello')
# cxn.close()

# ---- Bytes and strings ----
# b'abc'.decode() -> 'abc'      'abc'.encode() -> b'abc'
# text.split(' '), text.startswith('GET'), text[4:10]

# ---- JSON ----
# import json
# json.dumps({'a': 1}) -> '{"a": 1}'     json.loads('{"a": 1}') -> {'a': 1}

# ---- AES ----
# import cryptolib
# cryptolib.aes(key16, 2, iv16).encrypt(data)  # data: multiple of 16 bytes

# ---- MQTT ----
# from umqtt.simple import MQTTClient
# mqtt = MQTTClient(client_id=b'pico1', server=b'192.168.x.x', port=1883)
# mqtt.connect()
# mqtt.publish(b'temp/pico', b'21.5')
# mqtt.set_callback(my_function); mqtt.subscribe(b'temp/pico')
# mqtt.wait_msg()                  # wait     mqtt.check_msg()  # don't wait

# ---- I2C and LCD ----
# i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100_000)
# print(i2c.scan())                # LCD shows up as 62 (0x3E)
# from lcd1602 import LCD1602
# lcd = LCD1602(i2c, 2, 0)
# lcd.clear(); lcd.setCursor(0, 1); lcd.print('Hello')   # 16 chars per row

# ---- Quick test when you run this file ----
print('Temperature:', read_temp())
