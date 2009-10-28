from django.conf.urls.defaults import * #what all does this cover?
from django.conf import settings #set setting for media root for css files
#from django.contrib import databrowse
from nets.views import *
#from tut.views import *  
#versus 'import views' - one better than another?


#generic views
from django.views.generic.simple import direct_to_template
from django.views.generic import list_detail


urlpatterns = patterns('', #is the order these are in relevant to speed optimisation?
    # Uncomment this for admin:
     (r'^admin/', include('django.contrib.admin.urls')),
)

#network tools
urlpatterns += patterns('human.nets.views',
	(r'^nets/$', 'netbase'),
	(r'^nets/netinfo/$', 'netinfo'),
        (r'^nets/canviz/$', 'canviz_graph'),
        (r'^nets/netupload/$', 'netupload'),
        (r'^nets/netdeg/$', 'degreedist'),
        (r'^nets/netdisplay/$','netdisplay'),
        (r'^nets/hello/$', 'hello'), #what if these are all to be in 'nets'? how to specify at top?
        (r'^accounts/login/$', 'django.contrib.auth.views.login'),
        (r'^accounts/logout/$', 'django.contrib.auth.views.logout'), 
)

#to add css to development
if settings.DEBUG:
    urlpatterns += patterns('',
     (r'^site_media/(.*)$', 'django.views.static.serve',
      {'document_root': settings.BASE_REL('media')})
                            )


