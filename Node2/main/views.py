from django.shortcuts import render, redirect
import os

from django import template
from django.http import FileResponse, HttpResponse
import time
import Adafruit_DHT
import RPi.GPIO as GPIO
import sys
import signal
from pytz import timezone
from datetime import datetime

from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os, random


error_message = "ERROR"

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
        nowhum = error_message

    return nowhum

def get_cur_temp():

    sensor = Adafruit_DHT.DHT11
    pin = 21

    hum, tem = Adafruit_DHT.read_retry(sensor, pin)

    if hum is not None and tem is not None:
        nowtemp = "{0:0.1f}".format(tem)
    else:
        nowtemp = error_message
        
    return nowtemp

def get_cur_dis():
    
    #GPIO 핀
    TRIG = 20
    ECHO = 26

    MAX_DISTANCE_CM = 300
    MAX_DURATION_TIMEOUT = (MAX_DISTANCE_CM * 2 * 29.1)

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

    file = open("./main/media/result/history.txt", "a", encoding="utf-8")
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
    os.system('sudo uhubctl -l 2 -p 2 -a toggle')
    return render(request, 'main/index.html')

def save(request):
    make_history()  
    file_path = os.path.abspath("./main/media/result/")
    file_name = os.path.basename("./main/media/result/history.txt")
    fs = FileSystemStorage(file_path)
    response = FileResponse(fs.open(file_name, 'rb'),
                            content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="history.txt"'

    return response

def empty(request):
    tmp = get_cur_dis()
    return HttpResponse(tmp)

def index(request):
    os.system('sudo uhubctl -l 1-1 -p 2 -a off')
    os.system('sudo uhubctl -l 1-1 -p 3 -a off')
    return render(request, 'main/index.html')
