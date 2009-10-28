from django.conf.urls.defaults import *
from django.conf import settings #set setting for media root for css files
from nets.views import *


#generic views
from django.views.generic.simple import direct_to_template
from django.views.generic import list_detail


urlpatterns = patterns('',
    # Uncomment this for admin:
     (r'^admin/', include('django.contrib.admin.urls')),
)

#network tools
urlpatterns += patterns('human.nets.views',
	(r'^nets/$', 'netbase'),
	(r'^nets/netinfo/$', 'netinfo'),
        (r'^nets/netupload/$', 'netupload'),
        (r'^nets/netdeg/$', 'degreedist'),
        (r'^nets/netdisplay/$','netdisplay'),
)

#to add css to development
if settings.DEBUG:
    urlpatterns += patterns('',
     (r'^site_media/(.*)$', 'django.views.static.serve',
      {'document_root': settings.BASE_REL('media')})
                            )


