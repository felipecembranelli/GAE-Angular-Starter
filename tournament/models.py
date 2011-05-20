from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api import quota
from google.appengine.api import memcache

import logging
import datetime
import urllib
import random
#from aeoid import users
from google.appengine.api import users
from google.appengine.api import urlfetch
from django.utils import simplejson as json
from google.appengine.api.labs import taskqueue

#from django.utils.hashcompat import md5_constructor
from django.utils.html import escape
from operator import itemgetter

class User(db.Model):
    user_id = db.StringProperty(required=True)
    nickname = db.StringProperty(required=False)
    email = db.StringProperty(required=False)
    pic_url = db.StringProperty(required=False)

    @staticmethod
    def get_current_user(user_id, nickname=None, email=None):
        if not user_id:
            return None
        user = User.all().filter('user_id =', user_id).get()
        if not user:
            user = User(user_id = user_id, nickname = nickname, email = email)
            user.put()
        return user

    @staticmethod
    def login(user_id, nickname=None, email=None):
        user = User.get_current_user(user_id, nickname, email)
        if not user:
            raise Exception('Login unsuccessful')
        return user
    
    @staticmethod
    def is_current_user_admin():
        return False
    
    @staticmethod
    def create_logout_url(target):
        return '/logout?target=' + str(target)
    
    @staticmethod
    def create_login_url(target):
        return '/login?target=' + str(target)
    
class Session(db.Model):
    user_id = db.StringProperty(required=True)
    valid_until = db.DateTimeProperty(required=True)

    @staticmethod
    def create_session_for_user(user_id):
        Session.delete_session_for_user(user_id)
        valid_until = datetime.datetime.now() + datetime.timedelta(seconds = 86400)
        s = Session(user_id = user_id, valid_until = valid_until)
        s.put()
        return s.key().id()

    @staticmethod
    def delete_session_for_user(user_id):
        db.delete(Session.all().filter('user_id =', user_id))

    @staticmethod
    def get_session(session_id):
        try:
            s = Session.get_by_id(long(session_id))
            if s and s.valid_until > datetime.datetime.now():
                return s
        except Exception, e:
            logging.error('Error while getting session: '+str(e))
        return None

class Course(db.Model):
    name = db.StringProperty(required=True)
    
    @staticmethod
    def add_course(name, user):
        newCourse = Course(name=name)
        newCourse.put()
        
class App(db.Model):
    name = db.StringProperty(required=True)
    url = db.StringProperty(required=True)
    
    @staticmethod
    def add_app(name, user, url):
        newApp = App(name=name, url=url)
        newApp.put()

class TournamentHeat(db.Model):
    name = db.StringProperty(required=True)
    finished = db.BooleanProperty(default=False)
    created = db.DateTimeProperty(auto_now_add=True)
    jsonResult = db.TextProperty(required=False,default=None)
    
    @staticmethod
    def add_tournament_heat(name):
        newHeat = TournamentHeat(name=name)
        newHeat.put()

class Game(db.Model):
    tournamentHeat = db.ReferenceProperty(TournamentHeat, required=True)
    appX = db.ReferenceProperty(App, collection_name='XGames', required=False)
    appO = db.ReferenceProperty(App, collection_name='OGames', required=False)
    finished = db.BooleanProperty(default=False)
    boards = db.StringListProperty()
    jsongamelogs = db.StringListProperty()
    jsonResult = db.TextProperty(required=False,default=None)
    created = db.DateTimeProperty(auto_now_add=True)
    
    def log_move_and_save(self, move, turn, board, status):        
        d = dict()
        d['move'] = move
        d['turn'] = turn
        d['board'] = board
        d['status'] = status
        
        self.jsongamelogs.append(json.dumps(d))
        self.boards.append(board)
        self.put()
        #Add a list of strings to track the boards. 
    
    def game_results_string(self):
        result = ''
        for board in self.boards:
            result += board
            result += '\n'
        return 'Game history: \n'+result
    
    def game_boards_html(self):
        result = '<br>'
        for board in self.boards:
            result +='<br>'
            htmlboard = board.replace('\n', '<br>')
            result += htmlboard
        return 'Game history: <br>\n'+result
    
    def game_log_string(self):
        result = ''
        for jsongamelog in self.jsongamelogs:
            gamelog = json.loads(jsongamelog)
            
            result += 'move '  + str(gamelog['move']) + ' ' 
            result += 'turn '  + str(gamelog['turn']) + ' '
            result += 'board \n' + str(gamelog['board']) + ' \n'
            result += 'status ' + str(gamelog['status']['status']) + ' '
            result += '\n'
        return 'Game log: \n'+result
                