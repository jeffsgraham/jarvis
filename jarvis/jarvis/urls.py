from django.conf.urls import patterns, include, url
from inventory.views import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', Home.as_view()),
    # url(r'^blog/', include('blog.urls')),

    url(r'^room/([\w+]+)/$', RoomItemList.as_view()),
    url(r'^admin/', include(admin.site.urls)),
)
