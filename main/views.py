from django.shortcuts import render
import os

from django import template
import time
import Adafruit_DHT
import RPi.GPIO as GPIO
import sys
import signal
from pytz import timezone
from datetime import datetime

def get_cur_time():

    KST = timezone('Asia/Seoul')
    today = datetime.now()
    today = today.astimezone(KST)
    nowtime = today.strftime('%Y-%m-%d %H:%M')
    
    return nowtime

def get_cur_hum():

    sensor = Adafruit_DHT.DHT11
    pin = 21

    hum, tem = Adafruit_DHT.read_retry(sensor, pin)

    if hum is not None and tem is not None:
        nowhum = "{0:0.1f}".format(hum)
    else:
        nowhum = "Failed to get Humidity Data."

    return nowhum

def get_cur_temp():

    sensor = Adafruit_DHT.DHT11
    pin = 21

    hum, tem = Adafruit_DHT.read_retry(sensor, pin)

    if hum is not None and tem is not None:
        nowtemp = "{0:0.1f}".format(tem)
    else:
        nowtemp = "Failed to get Temperature Data."
        
    return nowtemp

def get_cur_dis():
    
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
        #171206 중간에 통신 안되는 문제 개선용      
        fail = False
        time.sleep(0.1)
        # 트리거를 10us 동안 High 했다가 Low로 함.
        # sleep 0.00001 = 10us
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        # ECHO로 신호가 들어 올때까지 대기
        timeout = time.time()
        while GPIO.input(ECHO) == 0:
            #들어왔으면 시작 시간을 변수에 저장
            pulse_start = time.time()
            if ((pulse_start - timeout)*1000000) >= MAX_DURATION_TIMEOUT:
                #171206 중간에 통신 안되는 문제 개선용        
                #continue
                fail = True
                break
            
        #171206 중간에 통신 안되는 문제 개선용        
        if fail:
            continue
        
        #ECHO로 인식 종료 시점까지 대기
        timeout = time.time()
        while GPIO.input(ECHO) == 1:
            #종료 시간 변수에 저장
            pulse_end = time.time()
            if ((pulse_end - pulse_start)*1000000) >= MAX_DURATION_TIMEOUT:
                distance = 0
                #171206 중간에 통신 안되는 문제 개선용        
                #continue
                fail = True
                break

        #171206 중간에 통신 안되는 문제 개선용        
        if fail:
            continue

        #인식 시작부터 종료까지의 차가 바로 거리 인식 시간
        pulse_duration = (pulse_end - pulse_start) * 1000000

        # 시간을 cm로 환산
        distance = (pulse_duration/2)/29.1
        #print(pulse_duration)
        #print('')
        # 자리수 반올림
        distance = round(distance, 2)

        #표시
        if distance < 5:
            sit_tf = "착석"
            break
        else:
            sit_tf = "부재"
            break

    GPIO.cleanup()
    return sit_tf

def make_history():
    c_time = get_cur_time()
    c_hum = get_cur_hum()
    c_temp = get_cur_temp()
    c_dis = get_cur_dis()

    c_output = f"{c_time};{c_hum}%;{c_temp}°C;{c_dis}\n"

    file = open("./history.txt", "a", encoding="utf-8")
    file.write(c_output)
    file.close

    print(c_output)

# Create your views here.
def index(request):
    os.system('sudo uhubctl -l 1-1 -p 2 -a off')
    os.system('sudo uhubctl -l 1-1 -p 3 -a off')
    make_history()
    return render(request, 'main/index.html')

def toggleled(request):
    os.system('sudo uhubctl -l 1-1 -p 2 -a toggle')
    return render(request, 'main/index.html')

def togglehum(request):
    os.system('sudo uhubctl -l 1-1 -p 3 -a toggle')
    return render(request, 'main/index.html')

def save(request):
    make_history()    
    return render(request, 'main/index.html')
