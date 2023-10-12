#!usr/bin/python3

from django import template
import time
import Adafruit_DHT
import RPi.GPIO as GPIO
import sys
import signal
from pytz import timezone
from datetime import datetime
import os

error_message = "ERROR"

minTemp = 0
maxTemp = 30

minHum = 0
maxHum = 100

globalTemp = 0.0
globalHum = 0.0
globalSit = False
globalLED = False
globalHum = False

register = template.Library()

@register.simple_tag
def get_cur_time():

    KST = timezone('Asia/Seoul')
    today = datetime.now()
    today = today.astimezone(KST)
    nowtime = today.strftime('%Y-%m-%d %H:%M')
    
    return nowtime

@register.simple_tag
def get_cur_hum():
    global globalHum

    sensor = Adafruit_DHT.DHT11
    pin = 21

    hum, tem = Adafruit_DHT.read_retry(sensor, pin)

    if hum is not None and tem is not None:
        nowhum = "{0:0.1f}".format(hum)
    else:
        nowhum = error_message

    globalHum = nowhum
    return nowhum

@register.simple_tag
def get_cur_temp():
    global globalTemp

    sensor = Adafruit_DHT.DHT11
    pin = 21

    hum, tem = Adafruit_DHT.read_retry(sensor, pin)

    if hum is not None and tem is not None:
        nowtemp = "{0:0.1f}".format(tem)
    else:
        nowtemp = error_message

    globalTemp = nowtemp
    return nowtemp

@register.simple_tag
def eval_hum():
    eval_prn = ""
    tmp_float = 0.0

    if globalHum == error_message:
        return error_message
    else:
        tmp_float = float(globalHum)

    if tmp_float < minHum:
        eval_prn = "가습기 작동이 필요합니다."
    elif tmp_float > maxHum:
        eval_prn = "제습기 작동이 필요합니다."
    else:
        eval_prn = "습도 상태가 정상입니다."

    return eval_prn

@register.simple_tag
def eval_temp():
    eval_prn = ""
    tmp_float = 0.0

    if globalTemp == error_message:
        return error_message
    else:
        tmp_float = float(globalTemp)

    if tmp_float < minTemp:
        eval_prn = "난방기 작동이 필요합니다."
    elif tmp_float > maxTemp:
        eval_prn = "냉방기 작동이 필요합니다."
    else:
        eval_prn = "온도 상태가 정상입니다."

    return eval_prn

@register.simple_tag
def get_cur_dis():
    global globalSit
    
    #GPIO 핀
    TRIG = 20
    ECHO = 26

    MAX_DISTANCE_CM = 300
    MAX_DURATION_TIMEOUT = (MAX_DISTANCE_CM * 2 * 29.1) #17460 # 17460us = 300cm

    distance = 0
    sit_tf = ""

    GPIO.setmode(GPIO.BCM)

    # Pin Setting
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    GPIO.output(TRIG, False)
    time.sleep(0.1)

    while True:   
        fail = False
        time.sleep(0.1)
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        timeout = time.time()
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
            if ((pulse_start - timeout)*1000000) >= MAX_DURATION_TIMEOUT:
                fail = True
                break
              
        if fail:
            continue
        
        timeout = time.time()
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
            if ((pulse_end - pulse_start)*1000000) >= MAX_DURATION_TIMEOUT:
                distance = 0
                fail = True
                break
      
        if fail:
            continue

        pulse_duration = (pulse_end - pulse_start) * 1000000

        distance = (pulse_duration/2)/29.1
        distance = round(distance, 2)

        if distance < 5:
            sit_tf = "착석"
            globalSit = True
            break
        else:
            sit_tf = "부재"
            globalSit = False
            break

    GPIO.cleanup()
    return sit_tf

@register.simple_tag
def get_cur_led():
    global globalLED
    led_rst = os.popen("sudo uhubctl | grep 'Port 2' | grep '0000' | awk '{print $4}'").read()

    if led_rst.strip() == "off":
        led_prn = "OFF"
        globalLED = False
    else:
        led_prn = "ON"
        globalLED = True

    return led_prn

@register.simple_tag
def get_cur_hum2():
    global globalHum
    led_rst = os.popen("sudo uhubctl | grep 'Port 2' | grep '0000' | awk '{print $4}'").read()

    if led_rst.strip() == "off":
        led_prn = "OFF"
        globalHum = False
    else:
        led_prn = "ON"
        globalHum = True

    return led_prn

@register.simple_tag
def eval_sit():
    eval_prn = ""
    if (globalSit):
        eval_prn = "현재 좌석을 사용중입니다."
    else:
        eval_prn = "현재 좌석을 사용중이지 않습니다."
        if(globalLED): eval_prn += "\nLED 조명을 끄셔도 됩니다."
        if(globalHum): eval_prn += "\n가습기를 끄셔도 됩니다."

    return eval_prn