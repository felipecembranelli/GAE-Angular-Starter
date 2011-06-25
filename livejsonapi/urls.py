
from django.conf.urls.defaults import *

urlpatterns = patterns('livejsonapi.views',
  (r'^$', 'index'),
  (r'^/$', 'index'),
  (r'^/index.html$', 'index'),
  (r'^/phones/phones.json$', 'phones'),
  (r'^/phones/wifi.json$', 'wifi'),
  (r'^/phones/xoom.json$', 'xoom'),  
  
)