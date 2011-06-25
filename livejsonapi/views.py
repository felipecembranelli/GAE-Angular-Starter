# Python imports
import logging
import datetime
import urllib
import sys

# AppEngine imports
from google.appengine.ext.webapp import template
from google.appengine.ext import db

#import django
from django import http
from django.utils import simplejson as json
from django.conf import settings

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from django.contrib.sites.models import Site
from django.utils.http import urlencode as django_urlencode


def phones(request):
    result = []
    phone = {"age": 0, "id": "wifi", "imageUrl": "img/phones/motorola-xoom-with-wi-fi.0.jpg", "name": "Motorola XOOM\u2122 with Wi-Fi", "snippet": "The Next, Next Generation\r\n\r\nExperience the future with Motorola XOOM with Wi-Fi, the world's first tablet powered by Android 3.0 (Honeycomb)."}
    result.append(phone)
    phone = {"age": 1, "id": "xoom", "imageUrl": "img/phones/motorola-xoom.0.jpg", "name": "MOTOROLA XOOM\u2122", "snippet": "The Next, Next Generation\n\nExperience the future with MOTOROLA XOOM, the world's first tablet powered by Android 3.0 (Honeycomb)."}
    result.append(phone)
    return http.HttpResponse(json.dumps(result))
 
def xoom(request):

    temp = '''
    {
    "additionalFeatures": "Front-facing camera. Sensors: proximity, ambient light, barometer, gyroscope.", 
    "android": {
        "os": "Android 3.0", 
        "ui": "Android"
    }, 
    "availability": [
        "Verizon"
    ], 
    "battery": {
        "standbyTime": "336 hours", 
        "talkTime": "24 hours", 
        "type": "Other (3250 mAH)"
    }, 
    "camera": {
        "features": [
            "Flash", 
            "Video"
        ], 
        "primary": "5.0 megapixels"
    }, 
    "connectivity": {
        "bluetooth": "Bluetooth 2.1", 
        "cell": "CDMA 800 /1900 LTE 700, Rx diversity in all bands", 
        "gps": true, 
        "infrared": false, 
        "wifi": "802.11 a/b/g/n"
    }, 
    "description": "MOTOROLA XOOM has a super-powerful dual-core processor and Android\u2122 3.0 (Honeycomb) \u2014 the Android platform designed specifically for tablets. With its 10.1-inch HD widescreen display, you\u2019ll enjoy HD video in a thin, light, powerful and upgradeable tablet.", 
    "display": {
        "screenResolution": "WXGA (1200 x 800)", 
        "screenSize": "10.1 inches", 
        "touchScreen": true
    }, 
    "hardware": {
        "accelerometer": true, 
        "audioJack": "3.5mm", 
        "cpu": "1 GHz Dual Core Tegra 2", 
        "fmRadio": false, 
        "physicalKeyboard": false, 
        "usb": "USB 2.0"
    }, 
    "id": "motorola-xoom", 
    "images": [
        "img/phones/motorola-xoom.0.jpg", 
        "img/phones/motorola-xoom.1.jpg", 
        "img/phones/motorola-xoom.2.jpg"
    ], 
    "name": "MOTOROLA XOOM\u2122", 
    "sizeAndWeight": {
        "dimensions": [
            "249.0 mm (w)", 
            "168.0 mm (h)", 
            "12.7 mm (d)"
        ], 
        "weight": "726.0 grams"
    }, 
    "storage": {
        "flash": "32000MB", 
        "ram": "1000MB"
    }
}    
    '''
    result = json.loads(temp)
    return http.HttpResponse(json.dumps(result))
    
def wifi(request):

    temp = '''
{
    "additionalFeatures": "Sensors: proximity, ambient light, barometer, gyroscope", 
    "android": {
        "os": "Android 3.0", 
        "ui": "Honeycomb"
    }, 
    "availability": [
        ""
    ], 
    "battery": {
        "standbyTime": "336 hours", 
        "talkTime": "24 hours", 
        "type": "Other ( mAH)"
    }, 
    "camera": {
        "features": [
            "Flash", 
            "Video"
        ], 
        "primary": "5.0 megapixels"
    }, 
    "connectivity": {
        "bluetooth": "Bluetooth 2.1", 
        "cell": "", 
        "gps": true, 
        "infrared": false, 
        "wifi": "802.11 b/g/n"
    }, 
    "description": "Motorola XOOM with Wi-Fi has a super-powerful dual-core processor and Android\u2122 3.0 (Honeycomb) \u2014 the Android platform designed specifically for tablets. With its 10.1-inch HD widescreen display, you\u2019ll enjoy HD video in a thin, light, powerful and upgradeable tablet.", 
    "display": {
        "screenResolution": "WXGA (1200 x 800)", 
        "screenSize": "10.1 inches", 
        "touchScreen": true
    }, 
    "hardware": {
        "accelerometer": true, 
        "audioJack": "3.5mm", 
        "cpu": "1 GHz Dual Core Tegra 2", 
        "fmRadio": false, 
        "physicalKeyboard": false, 
        "usb": "USB 2.0"
    }, 
    "id": "motorola-xoom-with-wi-fi", 
    "images": [
        "img/phones/motorola-xoom-with-wi-fi.0.jpg", 
        "img/phones/motorola-xoom-with-wi-fi.1.jpg", 
        "img/phones/motorola-xoom-with-wi-fi.2.jpg", 
        "img/phones/motorola-xoom-with-wi-fi.3.jpg", 
        "img/phones/motorola-xoom-with-wi-fi.4.jpg", 
        "img/phones/motorola-xoom-with-wi-fi.5.jpg"
    ], 
    "name": "Motorola XOOM\u2122 with Wi-Fi", 
    "sizeAndWeight": {
        "dimensions": [
            "249.1 mm (w)", 
            "167.8 mm (h)", 
            "12.9 mm (d)"
        ], 
        "weight": "708.0 grams"
    }, 
    "storage": {
        "flash": "32000MB", 
        "ram": "1000MB"
    }
}
    '''
    result = json.loads(temp)
    return http.HttpResponse(json.dumps(result))