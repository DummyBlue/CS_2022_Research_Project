from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls import include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
path('', views.index, name='index'),
path('toggleled/', views.toggleled),
path('togglehum/', views.togglehum),
path('save/', views.save),
]
