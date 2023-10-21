from django import template
from pytz import timezone
from datetime import datetime
import os
import requests

register = template.Library()

@register.simple_tag
def get_cur_time():
    KST = timezone('Asia/Seoul')
    today = datetime.now()
    today = today.astimezone(KST)
    nowtime = today.strftime('%Y-%m-%d %H:%M')
    
    return nowtime

@register.simple_tag
def get_node1():
    URL = 'http://node.bluefactor97.shop:9001/isnull/'
    response = requests.get(URL)
    if response.text.strip() == "착석":
        return "사용 중"
    else:
        return "사용 가능"
    #return "Unable"

@register.simple_tag
def get_node2():
    URL = 'http://node.bluefactor97.shop:8000/isnull/'
    response = requests.get(URL)
    if response.text.strip() == "착석":
        return "사용 중"
    else:
        return "사용 가능"
    #return "Unable"