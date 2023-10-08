# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import sys
import signal

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
print(sit_tf)