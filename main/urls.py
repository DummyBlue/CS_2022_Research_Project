from django.urls import path
from . import views

urlpatterns = [
path('', views.index, name='index'),
path('toggleled/', views.toggleled),
path('togglehum/', views.togglehum),
path('save/', views.save),
]
