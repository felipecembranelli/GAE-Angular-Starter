
from django.conf.urls.defaults import *

urlpatterns = patterns('livejsonapi.views',
  (r'^$', 'index'),
  (r'^/$', 'index'),
  (r'^/index.html$', 'index'),
  (r'^/get_user$', 'get_user'),
  (r'^/get_heat_result$', 'get_heat_result'),  
  (r'^/get_tournament_heats$', 'get_tournament_heats'),  
  (r'^/get_apps$', 'get_apps'),  
    
  (r'^/use/(?P<alternate>\w+)/game_status$', 'game_status'),
  (r'^/use/(?P<alternate>\w+)/get_next_move$', 'get_next_move'),
 
)