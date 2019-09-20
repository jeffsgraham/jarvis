"""jarvis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf.urls import url, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from rest_framework import routers, serializers, viewsets
from inventory import views

#

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'buildings', views.BuildingViewSet)
router.register(r'rooms', views.RoomViewSet)
router.register(r'manufacturers', views.ManufacturerViewSet)
router.register(r'models', views.ModelViewSet)
router.register(r'types', views.TypeViewSet)
router.register(r'items', views.ItemViewSet)
router.register(r'item_revisions', views.ItemRevisionViewSet)


urlpatterns = [
    #Standard view urls
    url(r'^$', views.MainList.as_view()),
    
    #AJAX view urls
    url(r'^inventory/item/all/$', views.AjaxMainList.as_view()),
    url(r'^inventory/item/search/(.*)/$', views.AjaxSearchItems.as_view()),
    url(r'^inventory/room/(?P<room_id>[\w+]+)/item/all/$', views.AjaxRoomView.as_view()),
    url(r'^inventory/item/([\w+]+)/details/$', views.AjaxItemDetail.as_view()),
    url(r'^inventory/item/([\w+]+)/edit/$', views.AjaxEditItem.as_view()),
    url(r'^inventory/item/([\w+]+)/archive/$', views.AjaxArchiveItem.as_view()),
    url(r'^inventory/item/([\w+]+)/move/$', views.AjaxMoveItem.as_view()),
    url(r'^inventory/item/([\w+]+)/attach/$', views.AjaxAttachItem.as_view()),
    url(r'^inventory/item/([\w+]+)/detach/$', views.AjaxDetachItem.as_view()),
    url(r'^inventory/room/([\w+]+)/item/add/$', views.AjaxAddItem.as_view()),
    url(r'^inventory/item/add/$', views.AjaxAddItem.as_view()),
    url(r'^inventory/item/attribute/add/$', views.AjaxAttributeAdd.as_view()),
    
    url('^accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html')),
    url('^accounts/logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html')),

    path('admin/', admin.site.urls),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/suggest/', views.ItemSuggestion.as_view())
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()