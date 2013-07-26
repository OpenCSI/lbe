from django.conf.urls import patterns, include, url
from django.contrib import admin
from directory import views
from account import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^/?$', 'directory.views.index'),
                       url(r'^directory/(?P<lbeObject_id>\d+)/(?P<page>\d+)$', 'directory.views.index'),
                       url(r'^ajax/directory/search/(?P<lbeObject_id>\d+)/(?P<search>.*)$',
                           'directory.views.searchAJAX'),
                       url(r'^directory/object/add/?$', 'directory.views.addObjectInstance'),
                       url(r'^directory/object/add/(?P<lbeObject_id>\d+)$', 'directory.views.addObjectInstance'),
                       url(r'^directory/object/delete/(?P<lbeObject_id>\d+)/(?P<objectName>.+)$',
                           'directory.views.deleteObjectInstance'),
                       url(r'^directory/object/manage/(?P<lbeObject_id>\d+)/(?P<objectName>.+)?/?(?P<type>[\w\s]+)?/?$',
                           'directory.views.manageObjectInstance'),
                       url(r'^directory/object/view/(?P<lbeObject_id>\d+)/(?P<objectName>.+)$',
                           'directory.views.viewObjectInstance'),
                       url(r'^directory/object/approval/(?P<lbeObject_id>\d+)/(?P<objectName>.+)$',
                           'directory.views.approvalObjectInstance'),
                       url(r'^directory/group/?$','directory.views.viewAllGroup'),
                       url(r'^directory/group/view/(?P<group_id>\d+)$','directory.views.viewGroup'),
                       url(r'^directory/group/manage/(?P<group_id>\d+)$','directory.views.manageGroup'),
                       url(r'^directory/group/delete/(?P<group_id>\d+)$','directory.views.deleteGroup'),

                       url(r'^config/?$', 'directory.views.index'),
                       url(r'^config/attribute/add/?$', 'config.views.addAttribute'),
                       url(r'^config/attribute/modify/(?P<attribute_id>\d+)?$', 'config.views.modifyAttribute'),
                       url(r'^config/attribute/remove/(?P<attribute_id>\d+)?$', 'config.views.removeAttribute'),
                       url(r'^config/object/add/?$', 'config.views.addObject'),
                       url(r'^config/object/list/?$', 'config.views.listObjects'),
                       url(r'^config/object/modify/(?P<obj_id>\d+)$', 'config.views.modifyObject'),
                       url(r'^config/object/addAttribute/(?P<obj_id>\d+)$', 'config.views.addAttributeToObject'),
                       url(r'^config/object/setAttributeOrder/(?P<obj_id>\d+)$',
                           'config.views.setAttributesOrderToObject'),
                       url(r'^config/object/modifyAttribute/modify/(?P<obj_id>\d+)/(?P<attr_id>\d+)$',
                           'config.views.modifyAttributeToObject'),

                       url(r'^config/reference/add/?$', 'config.views.addReference'),
                       url(r'^config/reference/modify/(?P<ref_id>\d+)?$', 'config.views.modifyReference'),
                       url(r'^config/reference/remove/(?P<ref_id>\d+)?$', 'config.views.removeReference'),

                       url(r'^config/acl/add/?$', 'config.views.addACL'),
                       url(r'^config/acl/manage/(?P<aclId>\d+)?$', 'config.views.manageACL'),
                       url(r'^config/acl/remove/(?P<aclId>\d+)?$', 'config.views.removeACL'),

                       url(r'^config/object/modify/(?P<obj_id>\d+)/(?P<attr_id>\d+)$',
                           'config.views.modifyInstanceAttribute'),
                       url(r'^config/object/removeAttribute/(?P<obj_id>\d+)/(?P<attr_id>\d+)$',
                           'config.views.removeInstanceAttribute'),
                       url(r'^config/script/add/?$', 'config.views.addScript'),
                       url(r'^config/script/manage/(?P<scriptId>\d+)?$', 'config.views.manageScript'),

                       url(r'^config/group/add/?$', 'config.views.addGroup'),
                       url(r'^config/group/manage/(?P<group_id>\d+)?$', 'config.views.manageGroup'),

                       url(r'^ajax/config/acl/check/(?P<query>.*)$', 'config.views.checkACL_AJAX'),
                       url(r'^ajax/config/object/showAttribute/(?P<attribute>\D+)?/(?P<value>\D+)?$',
                           'config.views.showAttributeAJAX'),
                       url(r'^ajax/directory/group/manage/user/(?P<group_name>.*)/(?P<name>.*)$',
                           'directory.views.viewUserObjectAJAX'),

                       (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'auth/login.html'}),
                       (r'^accounts/logout/$', 'django.contrib.auth.views.logout',
                        {'template_name': 'auth/logout.html'}),
                       url(r'^accounts/right/?$', 'account.views.right'),

                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),
)

#handler404 = views.page404
#handler500 = views.page500
