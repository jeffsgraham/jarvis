from django.conf.urls import patterns, include, url
from inventory.views import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #Standard view urls
    url(r'^$', MainList.as_view()),

    #AJAX view urls
    url(r'^ajax_main_list/$', AjaxMainList.as_view()),
    url(r'^ajax_room/([\w+]+)/$', AjaxRoomView.as_view()),
    url(r'^ajax_edit_item/([\w+]+)/$', AjaxEditItem.as_view()),
    url(r'^ajax_add_item/([\w+]+)/$', AjaxAddItem.as_view()),
    url(r'^ajax_add_item/$', AjaxAddItem.as_view()),

    #accounts and administrative urls
    (r'^accounts/login/$', Login.as_view()),#'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'registration/logout.html'}),
    url(r'^admin/', include(admin.site.urls)),
)
