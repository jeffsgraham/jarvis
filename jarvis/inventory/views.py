from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.generic.base import View
from django.views.generic import ListView, FormView, TemplateView
from django.contrib.auth.views import login as django_login
import json
from models import *
from forms import *

#Mixins Here

class LoginRequiredMixin(object):
    """Requires a logged in user for access any view classes that implement.
    
    """
    @classmethod
    def as_view(cls, **initkwargs):
        """Wraps the as_view() method in the login_required decorator function.
    
        """
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)

# Create your views here.

#class wrapper for django's login function
# alters incoming HTTP GET data to change the login form's
# redirect field to "/". This prevents issues with AJAX views.
class Login(View):
    """Class wrapper for django's login function.
        
    """
    def get(self, request, *args):
        """Changes the redirect url that is issued after successful login.
        
        Args:
            request: the HTTP request object.
            args: Additional args.

        Returns:
            The result of django's auth.login function executed on the altered 
                HTTP GET data.
        """
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
        """Passes on the django auth.login response

        """
        return django_login(request)


class MainList(LoginRequiredMixin, TemplateView):
    """Standard view for root inventory page.

        Attributes:
            template_name (string): The template to be rendered.
    """
    template_name = "template.html"

    def get_context_data(self, **kwargs):
        context = super(MainList, self).get_context_data(**kwargs)
        context['buildings'] = Building.objects.all()
        context['rooms'] = Room.objects.all()
        return context

class AjaxMainList(LoginRequiredMixin, View):
    """AJAX view that lists all active items, used in main page view."""
    def get(self, request, *args):
        items = Item.objects.filter(active=True)
        locationinfo = "All Items"
        pagetitle = "Jarvis Home"
        content_url = request.META['PATH_INFO']
        return render_to_response('ajax_room_view.html', locals())

class AjaxRoomView(LoginRequiredMixin, View):
    """AJAX View for room info requests. Lists all items in requested room."""
    def get(self, request, *args):
        room = get_object_or_404(Room, id=self.args[0])
        items = room.item_set.filter(active=True)
        locationinfo = room.building.abbrev + " " + str(room.number)
        pagetitle = "Room View"
        content_url = request.META['PATH_INFO']
        return render_to_response('ajax_room_view.html', locals())


class AjaxEditItem(LoginRequiredMixin, FormView):
    """AJAX view used to show an edit item dialog.
    
        Attributes:
            template_name (string): The template to be rendered.
            form_class (class): The form class to be used for data validation
            success_url (string): This is unused, statically set to prevent 
                errors in parent class methods.
            
    """
    template_name = 'ajax_edit_item.html'
    form_class = ItemForm
    success_url = "/" #unused

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
    """AJAX View used to show an add item dialog. Extends AjaxEditItem."""

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
