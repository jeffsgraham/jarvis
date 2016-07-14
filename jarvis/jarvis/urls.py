from django.conf.urls import patterns, include, url
from inventory.views import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #Standard view urls
    url(r'^$', MainList.as_view()),

    #AJAX view urls
    url(r'^inventory/item/all/$', AjaxMainList.as_view()),
    url(r'^inventory/item/search/(.*)/$', AjaxSearchItems.as_view()),
    url(r'^inventory/room/([\w+]+)/item/all/$', AjaxRoomView.as_view()),
    url(r'^inventory/item/([\w+]+)/details/$', AjaxItemDetail.as_view()),
    url(r'^inventory/item/([\w+]+)/edit/$', AjaxEditItem.as_view()),
    url(r'^inventory/item/([\w+]+)/archive/$', AjaxArchiveItem.as_view()),
    url(r'^inventory/item/([\w+]+)/move/$', AjaxMoveItem.as_view()),
    url(r'^inventory/item/([\w+]+)/attach/$', AjaxAttachItem.as_view()),
    url(r'^inventory/item/([\w+]+)/detach/$', AjaxDetachItem.as_view()),
    url(r'^inventory/room/([\w+]+)/item/add/$', AjaxAddItem.as_view()),
    url(r'^inventory/item/add/$', AjaxAddItem.as_view()),
    url(r'^inventory/item/attribute/add/$', AjaxAttributeAdd.as_view()),
    url(r'^inventory/iprange/all/$', AjaxIPRangeList.as_view()),
    url(r'^inventory/iprange/([\w+]+)/sweep/$', AjaxIPSweep.as_view()),


    #accounts and administrative urls
    (r'^accounts/login/$', Login.as_view()),#'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'registration/logout.html'}),
    url(r'^admin/', include(admin.site.urls)),
)
