import RPi.GPIO as GPIO
import time
import threading

GPIO.setmode(GPIO.BCM)

GPIO_TRIGGER = 5
GPIO_ECHO = 6

GPIO.setup(16, GPIO.IN)
GPIO.setup(20, GPIO.IN)
GPIO.setup(21, GPIO.IN)
GPIO.setup(12, GPIO.IN)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

def toggle(pin):
    if(GPIO.input(pin)):
        GPIO.output(pin, GPIO.LOW)
    else:
        GPIO.output(pin, GPIO.HIGH)

def blink():
    while True:
        if le.isSet() or ee.isSet():
            GPIO.output(17, GPIO.HIGH)
        if re.isSet() or ee.isSet():
            GPIO.output(22, GPIO.HIGH)
        time.sleep(0.5)
        if le.isSet() or ee.isSet():
            GPIO.output(17, GPIO.LOW)
        if re.isSet() or ee.isSet():
            GPIO.output(22, GPIO.LOW)
        time.sleep(0.5)

def honk():
    while True:
        honker = GPIO.input(12)
        if honker == False :
            GPIO.output(18, GPIO.HIGH)
        else:
            GPIO.output(18, GPIO.LOW)

def ultrasonic():
    startTime = time.time()
    stopTime = time.time()
    while True:
        GPIO.output(GPIO_TRIGGER, True)
        time.sleep(0.00001)
        GPIO.output(GPIO_TRIGGER, False)
        while GPIO.input(GPIO_ECHO) == 0:
            startTime = time.time()
        while GPIO.input(GPIO_ECHO) == 1:
            stopTime = time.time()
        timeElapsed = stopTime - startTime
        distance = (timeElapsed * 34300) / 2
        if distance < 40:
            GPIO.output(18, GPIO.HIGH)
        time.sleep(0.4)
        GPIO.output(18, GPIO.LOW)

le = threading.Event()
re = threading.Event()
ee = threading.Event()
t = threading.Thread(target=blink)
t.start()
h = threading.Thread(target=honk)
h.start()
us = threading.Thread(target=ultrasonic)
us.start()


try:
    while True:
        right = GPIO.input(21)
        middle = GPIO.input(20)
        left = GPIO.input(16)
        if left == False:
            if le.isSet():
                time.sleep(0.2)
                GPIO.output(17, GPIO.LOW)
                le.clear()
            else:
                re.clear()
                GPIO.output(22, GPIO.LOW)
                time.sleep(0.2)
                le.set()
        if right == False:
            if re.isSet():
                time.sleep(0.2)
                GPIO.output(22, GPIO.LOW)
                re.clear()
            else:
                le.clear()
                GPIO.output(17, GPIO.LOW)
                time.sleep(0.2)
                re.set()
        if middle == False:
            if ee.isSet():
                time.sleep(0.2)
                GPIO.output(17, GPIO.LOW)
                GPIO.output(22, GPIO.LOW)
                ee.clear()
            else:
                le.clear()
                re.clear()
                GPIO.output(17, GPIO.LOW)
                GPIO.output(22, GPIO.LOW)
                time.sleep(0.2)
                ee.set()

except KeyboardInterrupt:
    GPIO.cleanup()
