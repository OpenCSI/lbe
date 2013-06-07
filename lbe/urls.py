from django.conf.urls import patterns, include, url
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'directory.views.index'),
	url(r'^directory/?$', 'directory.views.index'),
	url(r'^ajax/directory/search/(?P<obj_id>\d+)/(?P<search>.*)$', 'directory.views.searchAJAX'),
    url(r'^directory/object/add/?$', 'directory.views.addObjectInstance'),
    url(r'^directory/object/add/(?P<lbeObject_id>\d+)$', 'directory.views.addObjectInstance'),
    url(r'^directory/object/delete/(?P<lbeObject_id>\d+)/(?P<objectName>[\w\d ]+)$', 'directory.views.deleteObjectInstance'),
    url(r'^directory/object/manage/(?P<obj_id>\d+)/(?P<uid>[\w\s]+)?/?(?P<type>[\w\s]+)?/?$', 'directory.views.manageObjectInstance'),
    url(r'^directory/object/view/(?P<obj_id>\d+)/(?P<objectName>[\w\d ]+)$', 'directory.views.viewObjectInstance'),

	url(r'^config/?$', 'directory.views.index'),
	url(r'^config/attribute/add/?$', 'config.views.addAttribute'),
	url(r'^config/object/add/?$', 'config.views.addObject'),
	url(r'^config/object/list/?$', 'config.views.listObjects'),
	url(r'^config/object/modify/(?P<obj_id>\d+)$', 'config.views.modifyObject'),
	url(r'^config/object/addattribute/(?P<obj_id>\d+)$', 'config.views.addObjectAttribute'),
	
	url(r'^config/reference/add/?$', 'config.views.addReference'),
	url(r'^config/reference/modify/(?P<ref_id>\d+)?$', 'config.views.modifyReference'),
	
	url(r'^ajax/config/reference/modify/(?P<ref_id>\d+)?$', 'config.views.modifyReferenceAJAX'),

	url(r'^config/object/modify/(?P<obj_id>\d+)/(?P<attr_id>\d+)$', 'config.views.modifyAttribute'),
	url(r'^config/script/add/?$', 'config.views.addScript'),
	url(r'^config/script/manage/(?P<scriptId>\d+)?$', 'config.views.manageScript'),
	
	url(r'^ajax/config/object/modify/(?P<obj_id>\d+)$', 'config.views.modifyObjectAJAX'),
	url(r'^ajax/config/attribute/modify/(?P<obj_id>\d+)/(?P<attr_id>\d+)$', 'config.views.modifyAttributeAJAX'),
	url(r'^ajax/config/object/showAttribute/(?P<attribute>\D+)?/(?P<value>\D+)?$', 'config.views.showAttributeAJAX'),
	
	url(r'^config/object/addattribute/(?P<obj_id>\d+)$', 'config.views.addObjectAttribute'),

    url(r'^/?(?P<lbeObject_id>\d+)?/?(?P<page>\d+)?$', 'directory.views.index'),
   
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
