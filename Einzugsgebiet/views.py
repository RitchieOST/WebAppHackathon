import os

from django import template
from django.http import HttpResponse
from django.shortcuts import render

#from Einzugsgebiet.main import weatherdatagraph


# Create your views here.




def start(request):

    return render(request, "HTML.html")



import requests
from django.shortcuts import render

def weather_map(request):
#    weatherdatagraph()

    lat, lon = 47.1416, 9.5215  # Beispiel: Vaduz
    api_key = "d46c1929646e1873f219924da550de5d"
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url).json()
    context = {
        "temp": response["main"]["temp"],
        "weather": response["weather"][0]["description"],
        "lat": lat,
        "lon": lon
    }

    return render(request, "HTML.html", context)



