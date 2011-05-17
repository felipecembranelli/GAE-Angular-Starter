
from django.conf.urls.defaults import *

urlpatterns = patterns('tictactoe.views',
#  (r'^$', 'index'),
  (r'^$', 'index'),
  (r'^/$', 'index'),
  (r'^/index.html$', 'index'),
  (r'^/get_supported_games$', 'get_supported_games'),
  (r'^/get_new_board$', 'get_new_board'), 
  (r'^/is_board_valid$', 'is_board_valid'), 
  (r'^/is_move_valid$', 'is_move_valid'),

  (r'^/game_status$', 'game_status'),    
  (r'^/get_next_move$', 'get_next_move'),

  (r'^/use/(?P<alternate>\w+)/game_status$', 'game_status'),
  (r'^/use/(?P<alternate>\w+)/get_next_move$', 'get_next_move'),

  #(r'^/use/(?P<string>\w+)/game_status$', 'game_status'),    
  #(r'^/use/(?P<string>\w+)/get_next_move$', 'get_next_move'),

#url(r'^tournament/(?P<tournament_id>\d+)', 'tournament'), 
#(r'^evaluate_interface/(?P<interface_id>\d+)/', 'evaluate_interface'),
     
 
)