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

# Local imports
import models
from forms import CourseForm, AppForm, TournamentHeatForm
import base64
from myutil import common

import tictactoe.TicTacToe as TicTacToe


def respond(request, user, template, params=None):
  """Helper to render a response, passing standard stuff to the response.

  Args:
    request: The request object.
    user: The User object representing the current user; or None if nobody
      is logged in.
    template: The template name; '.html' is appended automatically.
    params: A dict giving the template parameters; modified in-place.

  Returns:
    Whatever render_to_response(template, params) returns.

  Raises:
    Whatever render_to_response(template, params) raises.
  """
  ip = request.META['REMOTE_ADDR']
  if params is None:
    params = {}
  
  if user:
    params['user'] = user
    params['sign_out'] = models.User.create_logout_url('/')
    params['is_admin'] = (user.is_current_user_admin())
#  else:
#    params['sign_in'] = models.User.create_login_url(request.path)
  params['domain_url'] = common.getHostURI(request)
  params['page'] = template
  
  if not template.endswith('.html'):
    template += '.html'
  response = direct_to_template(request, template, params)
#  if user:
#    common.set_cookie(response = response, name = 'user_id', value = user.user_id)
  return response

def get_user(request):
  user = None
  if 'session_id' in request.COOKIES:
    session_id = request.COOKIES['session_id']
    session_id = base64.b64decode(session_id)
    logging.info('got session_id in cookies: '+str(session_id))
    session = models.Session.get_session(session_id)
    if session:
        user = models.User.get_current_user(session.user_id)
  if not user:
    logging.warning('User not logined')
  return user

#Move this to a template. 
def auth_error(domain_url):
  return http.HttpResponse(content = 
      '''<html><body>
          You are not logined! You can <a class="rpxnow" onclick="return false;" href="https://pivotalexpert.rpxnow.com/openid/v2/signin?token_url='''+domain_url+'''%2Frpx.php">sign in here</a>!
          <script type="text/javascript">
            var rpxJsHost = (("https:" == document.location.protocol) ? "https://" : "http://static.");
            document.write(unescape("%3Cscript src='" + rpxJsHost + "rpxnow.com/js/lib/rpx.js' type='text/javascript'%3E%3C/script%3E"));
          </script>
          <script type="text/javascript">
            RPXNOW.overlay = true;
            RPXNOW.language_preference = 'en';
          </script>
         </body>
         </html>''', status = 401)

def index(request):
  logging.info('cookies: '+str(request.COOKIES))
  user = get_user(request)
  #if not user:
  #  return auth_error(common.getHostURI(request))
  courses = models.Course.all()
  apps = models.App.all()
  tournamentHeats = models.TournamentHeat.all()
  return respond(request, user, 'index', {'next': '/', 'courses':courses, 'apps':apps, 'tournamentHeats':tournamentHeats})
  
def add_course(request):
  #Fetch name parameter from GET request and create new course as an example
  logging.info('Adding a course')
  user = get_user(request)
  #if not user:
  #  return auth_error(common.getHostURI(request))
  models.Course.add_course(name='New Course', user=user)
  return http.HttpResponseRedirect('/')
  # courses = models.Course.all()
  # return respond(request, user, 'index', {'next': '/', 'courses':courses})

def add_app(request):
  #Fetch name parameter from GET request and create new course as an example
  logging.info('Adding an app')
  user = get_user(request)
  #if not user:
  #  return auth_error(common.getHostURI(request))
  models.App.add_app(name='New Game App', user=user, url='DEFAULT_TICTACTOE')#'http://deli.appspot.com/tictactoe'
  return http.HttpResponseRedirect('/')
  #return respond(request, user, 'index', {'next': '/', 'courses':courses, 'apps':apps})
  
def add_tournament_heat(request):
  #Fetch name parameter from GET request and create new course as an example
  logging.info('Adding a tournament heat.')

  models.TournamentHeat.add_tournament_heat(name='New tournament heat')    
  return http.HttpResponseRedirect('/')
  
def edit_app(request, id=None):
    return edit_entity(request, id, c = models.App, useForm = AppForm)

def edit_course(request, id=None):
    return edit_entity(request, id, c = models.Course, useForm = CourseForm)

def edit_tournament_heat(request, id=None):
    return edit_entity(request, id, c = models.TournamentHeat, useForm = TournamentHeatForm)

def view_heat_result(request, id=None):
    tournamentHeat = None
    if not id:
        logging.info('Please pass in a tournament heat ID')
        return http.HttpResponseNotFound('No tournament heat id passed in.')
    
    tournamentHeat = models.TournamentHeat.get_by_id(int(id))
    if not tournamentHeat: 
        logging.info('No such tournament heat.')
        return http.HttpResponseNotFound('No such tournament heat.')
    
    heatResult = tournamentHeat.jsonResult
    heatResultDict = json.loads(heatResult)
    
    appNames = heatResultDict['appNames']
    ids = heatResultDict['ids']
    points = heatResultDict['points']
    temp = heatResultDict['matchResults']
    logging.warn('temp = %s', temp)

    matchResults = []   
    
    headerRow = []
    headerRow.append('App')
    headerRow.append('Points')
    
    logging.warn('********** ids %s',ids)
    for k in ids: #temp.keys(): 
        headerRow.append(appNames[k]+' ('+str(k)+')') 
    
    matchResults.append(headerRow)
    #ids = temp.keys()
    
    for i in ids:
      row = []
      row.append(appNames[i]+' ('+str(i)+')')
      row.append(points[i])
      dict = temp[i]
      for k in ids:
        result = None
        if dict.has_key(k):
          result = {'n':dict[k], 'i':i, 'k':k}
        else: result = '*'
        row.append(result)
      matchResults.append(row)
        #for y in v:
        #    row.append(y)
        #matchResults.append(row)

            
    #Build result row dicts and insert into resultRowDict list
    
    #Create dictionary and render to template
    return respond(request, None, 'heatresult', {'heatID':id,'matchResults':matchResults,'heatResult':heatResult,'appNames':appNames})

def check_app(request, id=None):
    app = None
    if not id:
        logging.info('Please pass in an app ID')
        return http.HttpResponseNotFound('No app id passed in.')
    
    app = models.App.get_by_id(int(id))
    if not app: 
        logging.info('No such app.')
        return http.HttpResponseNotFound('No such app.')
    
    message = 'Preparing to check app <br> '
    game_status_result = None
    get_next_move_result = None
    board = 'X**\n***\n***'
    try:
        game_status_result = fetch_from_url(app.url,'game_status', {'board':board})
        message += 'Result from /game_status was '+str(game_status_result)+'<br>'
    except:
        e = sys.exc_info()[1]
        message += 'Received an error from /game_status '+str(e)+'<br>'
    
    try:
        get_next_move_result = fetch_from_url(app.url,'get_next_move', {'board':board})
        message += 'Result from /get_next_move was '+str(get_next_move_result)+'<br>'
    except:
        e = sys.exc_info()[1]
        message += 'Received an error from /get_next_move '+str(e)+'<br>'
             
    #return http.HttpResponseNotFound(message)
    #Create dictionary and render to template
    return respond(request, None, 'check_app', { 'app':app,'game_status_result':game_status_result, 'get_next_move_result':get_next_move_result})
      
def fetch_from_url(appurl, function, jsonRequestDict):
    logging.debug('Checking an app')
    
    #return local_return()
    if appurl[0:8]=='DEFAULT_':
        return TicTacToe.local_return(appurl, function, jsonRequestDict)
       
    url = appurl+'/'+function
       
    requestJSON = json.dumps(jsonRequestDict)
    params = urllib.urlencode({'jsonrequest': requestJSON})
    
    jsonresponse = ''
    request_time = datetime.datetime.now()
    response_time = datetime.datetime.now()
    logging.debug('fetching from '+url)
    try:
        deadline = 10
        result = urlfetch.fetch(url=url,
                                payload=params,
                                #method=urlfetch.GET,
                                method=urlfetch.POST,
                                deadline=deadline,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'})

        response_time = datetime.datetime.now()
        delta = response_time - request_time
        microseconds = delta.seconds * 1000000 + delta.microseconds
        jsonresponse = result.content
        logging.info('url %s returned json %s in %s microseconds',url,jsonresponse, microseconds)
        return json.loads(jsonresponse)
    
    except:
        e = sys.exc_info()[1]
        logging.warning('Catching url fetch or JSON parsing problem %s while calling url %s with parameters %s received %s',e,url, params, jsonresponse)
        return {'error': 'Problem parsing passed in json.'+str(e)}

#Need to pass in full apps to play and record game with app references
#Need tournament as well. 
def play_game(playerX, playerO, referee, tournamentHeat):
    
        #Find existing game
        game = models.Game.all().filter('appX=',playerX).filter('appO=',playerO).filter('tournamentHeat=',tournamentHeat).get()
        if not game:
            game = models.Game(appX=playerX,appO=playerO,tournamentHeat=tournamentHeat)
            game.put()
        
        player = {'X':playerX, 'O': playerO}
        result = fetch_from_url(referee.url,'get_new_board', {})
        logging.info('Retrieving new board %s', result)
        
        if not 'board' in result:
            logging.error("No board key returned from referee %s result was %s", referee.url, result)
        
        board = result['board']      
        
        moves = []
        move = None
                
        for i in range(9):
    
            result = fetch_from_url(referee.url, 'game_status', {'board':board})
            logging.debug(result)
            
            if not 'turn' in result:
                 logging.error("No turn key returned from referee %s result was %s", referee.url, result)
                                
            turn = result['turn']       
            otherPlayer = 'O'
            if turn==otherPlayer: 
                otherPlayer = 'X'

            #Add timeout         
            result = fetch_from_url(player[turn].url,'get_next_move', {'board':board})
            
            if not 'move' in result:
                logging.info('player %s did not return a move key in result %s',player[turn].url,result)
                game.log_move_and_save(move=i,turn=turn, board='No Reply',status=otherPlayer+'  WON')
                return otherPlayer+' WON'
                        
            move = result['move']
            moves.append(move)

            result = fetch_from_url(referee.url,'is_move_valid', {'board':board,'move':move})
            
            if not 'valid' in result:
                logging.error('No valid key returned when calling is_move_valid from referee %s got result %s', referee.url, result)
            
            isMoveValid = result['valid']
            if not isMoveValid:
                game.log_move_and_save(move=i,turn=turn, board='Not Valid->'+move,status=otherPlayer+'  WON')                
                return otherPlayer+' WON'

            result = fetch_from_url(referee.url,'game_status', {'board':move})
            logging.info(result)
            
            #Need error checking here. 
            status = result
            if status['status']!='PLAYING':
              #put a break here rather than return. 
              #print '\n'+status['status']
              # update game and return
              # game.finished = db.BooleanProperty(default=False)
              # game.jsonResult = db.TextProperty(required=False,default=None)
              game.log_move_and_save(move=i,turn=turn, board=move,status=status)
              return status['status']
            
            game.log_move_and_save(move=i,turn=turn, board=move,status=status)
            board = move
            
        return 'No result'

def run_tournament_heat(request,id=None):
    
    tournamentHeat = None
    if not id:
        logging.info('Please pass in a tournament ID')
        return http.HttpResponseNotFound('No tournament id passed in.')
    
    tournamentHeat = models.TournamentHeat.get_by_id(int(id))
    if not tournamentHeat: 
        logging.info('No such tournament heat.')
        return http.HttpResponseNotFound('No such tournament heat.') 
    
    #Enqueue live_run_tournament_heat
    taskqueue.add(url='/live_run_tournament_heat/'+str(id)+'/',
                  queue_name='tournament-queue') 
#                  params={'id': int(id)})
    logging.info('Enqueued tournament heat '+str(id))
    return http.HttpResponseNotFound('Enqueued tournament heat '+str(id)) 
   
#Move this to the models class since not request object interaction.  
#To be enqueued
def live_run_tournament_heat(request, id=None):

    tournamentHeat = None
    if not id:
        logging.info('Please pass in a tournament ID')
        return http.HttpResponseNotFound('No tournament id passed in.')
    
    tournamentHeat = models.TournamentHeat.get_by_id(int(id))
    if not tournamentHeat: 
        logging.info('No such tournament heat.')
        return http.HttpResponseNotFound('No such tournament heat.') 
    
    result = run_round(tournamentHeat)
    
    return http.HttpResponse(json.dumps(result))

def view_game_result(request, tournamentHeatID=None, appXID=None, appOID=None):  
    
    tournamentHeat = None
    appX = None
    appO = None
    
    if not tournamentHeatID or not appXID or not appOID:
        logging.warning('Please pass in a valid tournamentHeatID, appXID, and appOID')
        return http.HttpResponseNotFound('Please pass in a valid tournamentHeatID, appXID, and appOID: /view_game_result/tournamentHeat/id/appXID/id/appOID/id')
    
    tournamentHeat = models.TournamentHeat.get_by_id(int(tournamentHeatID))
    if not tournamentHeat: 
        logging.warning('No such tournament heat.')
        return http.HttpResponseNotFound('No such tournament heat.') 
    
    appX = models.App.get_by_id(int(appXID))
    if not appX: 
        logging.warning('No such app for appXID.')
        return http.HttpResponseNotFound('No such app for appXID') 
    
    appO = models.App.get_by_id(int(appOID))
    if not appO: 
        logging.warning('No such app for appOID.')
        return http.HttpResponseNotFound('No such app for appOID') 
    
    game = models.Game.all().filter('tournamentHeat = ', tournamentHeat).filter('appX = ',appX).filter('appO = ',appO).get()
    if not game:
        logging.warning('No game found for th %s appxid %s appoid %s',tournamentHeatID, appXID, appOID )
        return http.HttpResponseNotFound('No game found for th '+tournamentHeatID+' appxid '+appXID+' appoid '+appOID ) 
        
    #result = run_round(tournamentHeat)
    #result = 'Under Development'
    #result = game.game_results_string()
    result = game.game_boards_html()
    #result = game.game_log_string()
    return http.HttpResponse(result)
           

def run_round(tournamentHeat, players=None):
    tournamentHeat.finished = False
    tournamentHeat.put()
    
    referee = models.App(name='Referee', url='DEFAULT_TICTACTOE')
    
    if not players:
        players = {}
        apps = models.App.all()
        for app in apps: 
            players[app.key().id()] = app
    
    appNames = {}
    for appID, app in players.iteritems():
        appNames[appID] = app.name
    
    if len(players)<2: 
        return http.HttpResponseNotFound('Less than 2 apps registered.') 
            
    points = {}
    losses = {}
    matchResults = {}
    
    #Change this to use App ID's and remove need for player list
    for app in apps: 
        app_id = app.key().id()
        points[app_id]=0
        losses[app_id]=0
        matchResults[app_id] = {}
        
    for appX in apps:
        for appY in apps:
            x = appX.key().id()
            y = appY.key().id()
            if x!=y:
                #result = self.head_to_head(players[x], players[y], TicTacToe())
                logging.info("playing %s against %s with referee %s", players[x].url, players[y].url, referee.url)
                result = play_game(players[x], players[y], referee, tournamentHeat)
                
                if 'X' in result: 
                    points[x]+=1
                    losses[y]+=1
                    matchResults[x][y] = '1'
                elif 'O' in result: 
                    points[y]+=1
                    losses[x]+=1
                    matchResults[x][y] = '-1' 
                else:
                    points[x]+=0.5
                    points[y]+=0.5
                    matchResults[x][y] = '0.5'
        
        #print '\n'
        #for k in points: 
        #  print k, 'scored', points[k], 'points', losses[k],'losses',players[k].get_name()

        #sorted_list.sort(key=lambda x: x[0]) # sort by key
        #appIDs = []
        appIDs = [x for x in points.iteritems()] 
        appIDs.sort(key=lambda x: x[1]) # sort by value
        appIDs.reverse()

        ids = []
        for id in appIDs: ids.append(str(id[0]))
        #logging.warn('******* sorted appIDs %s', appIDs)
        
    result = {'points':points,
              'losses':losses,
              'appNames':appNames,
              'matchResults':matchResults,
              'appIDs':appIDs,
              'ids':ids}
    
    tournamentHeat.jsonResult = json.dumps(result)
    tournamentHeat.finished = True
    tournamentHeat.put()
    return result

    #Update the view to list supported and unsupported interfaces.
    #return respond(request,None,'tournamentresult', {'results':results})

def edit_entity(request, id=None, c = models.Course, useForm = CourseForm):
 
  entity = None
  if id: 
      id = int(id)
  
  entity = None
  creatingNew = False
  
  if not id:
    creatingNew = True
    
  else:
    entity = c.get_by_id(int(id))
    if entity is None:
      return http.HttpResponseNotFound('No such entity.') 
 
  form = useForm(data=request.POST or None, instance=entity)

  if not request.POST:
    return respond(request, None, 'edit_entity', {'form': form, 'entity': entity, 'creatingNew': creatingNew})
  
  errors = form.errors
  if not errors:
    try:
        entity = form.save(commit=False)
    except ValueError, err:
        errors['__all__'] = unicode(err)
    if errors:
      return respond(request, None, 'edit_entity', {'form': form, 'entity': entity, 'creatingNew': creatingNew})
  else:
      logging.info("There were form.errors. %s", errors)

  if creatingNew:
    pass
    #interface.editor = currentPlayer
 
  entity.put()
  return http.HttpResponseRedirect('/')
