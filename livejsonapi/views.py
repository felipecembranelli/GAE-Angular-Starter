# Python imports
import logging
import datetime
import urllib
import sys

# AppEngine imports
#from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.ext.db import djangoforms
from google.appengine.api import memcache
from google.appengine.api import quota
from google.appengine.api.labs import taskqueue

#import django
from django import http
from django import shortcuts
from django.utils import simplejson as json
from django.conf import settings

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from django.contrib.sites.models import Site
from django.utils.http import urlencode as django_urlencode


import tournament.models as models

def get_user(request):
    #user = models.User.all().get()
    result = {}
    #result['nickname'] = "Haven't finished this yet."
    result = {"nickname": "live tommy"}
    return http.HttpResponse(json.dumps(result))
 
def get_heat_result(request):
    #heat = models.TournamentHeat.all().get()
    result = {}
    result = {"appIDs": [[2, 1], [1, 1]], "losses": {"1": 1, "2": 1}, "ids": ["2", "1"], "points": {"1": 1, "2": 1}, "appNames": {"1": "Test from live app 1", "2": "Test from live app 2"}, "matchResults": {"1": {"2": "1"}, "2": {"1": "1"}}}
    
    return http.HttpResponse(json.dumps(result)) 
    
def get_apps(request):
    apps = models.App.all()
    result = {}
    for app in apps: 
        result['name'] = app.name
        result['id'] = app.key().id()
        
    return http.HttpResponse(json.dumps(result))
  
