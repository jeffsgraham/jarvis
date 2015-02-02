from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.generic.base import View
from django.views.generic import ListView, FormView
from django.contrib.auth.views import login as django_login
import json
from models import *
from forms import *

#Mixins Here

#Provides @login_required decorator-like functionality for class based views
class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)

# Create your views here.

#class wrapper for django's login function
# alters incoming HTTP GET data to change the login form's
# redirect field to "/". This prevents issues with AJAX views.
class Login(View):
    
    #change the redirect url that is issued after successful login
    def get(self, request, *args):
        #Note: the original GET dictionary is immutable,
        # so we make a copy to alter it. Alternately we 
        # could have changed the _mutable property.
        get_copy = request.GET.copy()
        get_copy['next'] = "/"
        
        #set _mutable back to prevent alteration by other functions
        get_copy._mutable = request.GET._mutable 
        request.GET = get_copy

        return django_login(request)

    def post(self, request, *args):
        return django_login(request)


#view for root inventory page. Lists all items
class MainList(LoginRequiredMixin, ListView):
    template_name = "template.html"
    model = Item

    def get_context_data(self, **kwargs):
        context = super(MainList, self).get_context_data(**kwargs)
        context['buildings'] = Building.objects.all()
        context['rooms'] = Room.objects.all()
        return context

    def get_query_set(self):
        return Item.objects.all()

class AjaxMainList(LoginRequiredMixin, View):
    def get(self, request, *args):
        items = Item.objects.filter(active=True)
        locationinfo = "All Items"
        pagetitle = "Jarvis Home"
        content_url = request.META['PATH_INFO']
        return render_to_response('ajax_room_view.html', locals())

#View for ajax room info requests. Lists all items in requested room as well as 
 #room info
class AjaxRoomView(LoginRequiredMixin, View):
    def get(self, request, *args):
        room = get_object_or_404(Room, id=self.args[0])
        items = room.item_set.filter(active=True)
        locationinfo = room.building.abbrev + " " + str(room.number)
        pagetitle = "Room View"
        content_url = request.META['PATH_INFO']
        return render_to_response('ajax_room_view.html', locals())


class AjaxEditItem(LoginRequiredMixin, FormView):
    template_name = 'ajax_edit_item.html'
    form_class = ItemForm
    success_url = "/" #unused, just here to prevent errors due to this being ajax called

    def get_context_data(self, **kwargs):
        context = super(AjaxEditItem, self).get_context_data(**kwargs)
        context['item'] = get_object_or_404(Item, id=self.args[0])
        context['title'] = "Edit Item Form"
        context['submit_url'] = "/ajax_edit_item/" + context['item'].id + "/"
        return context

    def get_form(self, form_class=None):
        item = get_object_or_404(Item, id=self.args[0])
        return ItemForm(self.request.POST, instance=item)

    def form_invalid(self, form):
        return HttpResponse("Invalid Form Data", content_type="text/plain")


    def form_valid(self, form):
        form.save()
        return HttpResponse("Saved", content_type="text/plain")

class AjaxAddItem(AjaxEditItem):
    def get_context_data(self, **kwargs):
        context = super(AjaxEditItem, self).get_context_data(**kwargs) #grandparent's method
        if(len(self.args) >= 1): #if room id has been passed
            context['room'] = get_object_or_404(Room, id=self.args[0])
        room_id = (context['room'].id + "/") if ('room' in context) else ("")
        context['title'] = "Add Item Form"
        context['submit_url'] = "/ajax_add_item/" + room_id
        return context

    def get_form(self, form_class=None):
        return ItemForm(self.request.POST)
