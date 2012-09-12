from django.conf.urls import patterns, include, url
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'directory.views.index'),
	url(r'^directory/?$', 'directory.views.index'),
	url(r'^directory/object/add/?$', 'directory.views.addObjectInstance'),
	url(r'^directory/object/add/(?P<lbeObject_id>\d+)$', 'directory.views.addObjectInstance'),
	url(r'^config/?$', 'directory.views.index'),
	url(r'^config/attribute/add/?$', 'config.views.addAttribute'),
	url(r'^config/object/add/?$', 'config.views.addObject'),
	url(r'^config/object/list/?$', 'config.views.listObjects'),
	url(r'^config/object/modify/(?P<obj_id>\d+)$', 'config.views.modifyObject'),
	url(r'^ajax/config/object/modify/(?P<obj_id>\d+)$', 'config.views.modifyObjectAJAX'),
	url(r'^ajax/config/object/showAttribute/(?P<attribute>\D+)?/(?P<value>\D+)?$', 'config.views.showAttributeAJAX'),
	url(r'^config/object/addattribute/(?P<obj_id>\d+)$', 'config.views.addObjectAttribute'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
