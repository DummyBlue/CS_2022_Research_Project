from django.shortcuts import render, redirect
import os
from django.http import HttpResponse


def index(request):
    return render(request, 'main/index.html')