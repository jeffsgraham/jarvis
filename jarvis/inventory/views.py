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
        context['rooms'] = Room.objects.all().order_by('number')
        return context

class AjaxMainList(LoginRequiredMixin, View):
    """AJAX view that lists all active, unattached items. Used in main page view."""
    def get(self, request, *args):
        items = Item.objects.filter(active=True, item=None)
        pagetitle = "Jarvis Home"
        content_url = request.META['PATH_INFO']
        return render_to_response('ajax_room_view.html', locals())


class AjaxSearchItems(LoginRequiredMixin, View):
    """AJAX view that lists all active items that match the given search terms."""
    def get(self, request, *args):
        items = Item.objects.raw_query({'$text': {'$search': self.args[0]}})
        pagetitle = "Results for " + self.args[0]
        content_url = request.META['PATH_INFO']
        disable_add = True
        return render_to_response('ajax_room_view.html', locals())

class AjaxIPRangeList(LoginRequiredMixin, View):
    """AJAX view that lists saved IPRanges."""
    def get(self, request, *args):
        ranges = IPRange.objects.all()
        pagetitle = "IP Ranges"
        content_url = request.META['PATH_INFO']
        return render_to_response('ajax_iprange_view.html', locals())

class AjaxIPSweep(LoginRequiredMixin, View):
    """AJAX view that lists results of IPRange sweep."""
    def get(self, request, *args):
        iprange = get_object_or_404(IPRange, id=self.args[0])
        results = iprange.sweep()
        pagetitle = "IP Sweep Results for " + str(iprange)
        content_url = request.META['PATH_INFO']
        return render_to_response('ajax_ipsweep_view.html', locals())

class AjaxItemDetail(LoginRequiredMixin, View):
    """AJAX view that shows item details."""
    def get(self, request, *args):
        item = get_object_or_404(Item, id=self.args[0])
        content_url = request.META['PATH_INFO']
        return render_to_response('ajax_detail_view.html', locals())

class AjaxRoomView(LoginRequiredMixin, View):
    """AJAX View for room info requests. Lists all items in requested room."""
    def get(self, request, *args):
        room = get_object_or_404(Room, id=self.args[0])
        items = room.item_set.filter(active=True, item=None)
        pagetitle = room.building.abbrev + " " + str(room.number)
        
        content_url = request.META['PATH_INFO']
        return render_to_response('ajax_room_view.html', locals())

class AjaxAttributeAdd(LoginRequiredMixin, View):
    """AJAX View for item attribute suggestions form."""
    def get(self, request, *args):
        attrSuggestions = Attribute.objects.all().order_by("name")
        return render_to_response('ajax_item_attribute_form.html', locals())

class AjaxEditItem(LoginRequiredMixin, FormView):
    """AJAX view used to show an edit item dialog.
    
        Attributes:
            template_name (string): The template to be rendered.
            form_class (class): The form class to be used for data validation
            success_url (string): This is unused, statically set to prevent 
                errors in parent class methods.
            
    """
    template_name = 'ajax_item_form.html'#'ajax_edit_item.html'
    form_class = ItemForm2
    success_url = "/" #unused

    def get_context_data(self, **kwargs):
        context = super(AjaxEditItem, self).get_context_data(**kwargs)
        context['itemTypes'] = Type.objects.all()
        context['manufacturers'] = Manufacturer.objects.all()
        context['models'] = Model.objects.all()
        context['attrSuggestions'] = Attribute.objects.all().order_by("name")

        context['item'] = get_object_or_404(Item, id=self.args[0])
        context['title'] = "Edit Item Form"
        context['submit_url'] = "/inventory/item/" + context['item'].id + "/edit/"
        return context

    def get_form(self, form_class=None):
        item = get_object_or_404(Item, id=self.args[0])
        return form_class(self.request.POST, instance=item)

    def form_invalid(self, form):
        return HttpResponse("Invalid Form Data", content_type="text/plain")

    def form_valid(self, form):
        form.save(user=self.request.user)
        return HttpResponse("Saved", content_type="text/plain")

class AjaxAddItem(AjaxEditItem):
    """AJAX View used to show an add item dialog. Extends AjaxEditItem."""

    def get_context_data(self, **kwargs):
        context = super(AjaxEditItem, self).get_context_data(**kwargs) #grandparent's method

        context['itemTypes'] = Type.objects.all()
        context['manufacturers'] = Manufacturer.objects.all()
        context['models'] = Model.objects.all()

        if(len(self.args) >= 1): #if room id has been passed
            context['room'] = get_object_or_404(Room, id=self.args[0])
        room_id = ("room/" + context['room'].id + "/") if ('room' in context) else ("")
        context['title'] = "Add Item Form"
        context['submit_url'] = "/inventory/" + room_id + "item/add/"
        return context

    def get_form(self, form_class=None):
        return form_class(self.request.POST)

class AjaxMoveItem(LoginRequiredMixin, FormView):
    form_class = MoveItemForm
    success_url = "/"

    def get_form(self, form_class=None):
        item = get_object_or_404(Item, id=self.args[0])
        return form_class(self.request.POST, instance=item)

    def form_invalid(self, form):
        alert_type = "danger"
        #build error message
        item = form.instance
        itemType = str(item.itemType)
        room_name = str(item.room)
        message = "Couldn't move " + itemType + " to " + room_name + ". Invalid Form Data."
        return render_to_response('ajax_move_item_confirm.html', locals())

    def form_valid(self, form):
        message = ""
        item = form.instance
        item_name = str(item.manufacturer) + " " + str(item.itemType)
        room_name = str(item.room)
        if form.has_changed():
            form.save(user=self.request.user)
            #build confirm message
            alert_type = "success"
            message = item_name + " moved to " + room_name
        else:
            alert_type = "warning"
            message = item_name + " is already in " + room_name
        return render_to_response('ajax_move_item_confirm.html', locals())

class AjaxAttachItem(AjaxMoveItem):
    form_class = AttachItemForm
    success_url = "/"

    def form_invalid(self, form):
        alert_type = "danger"
        #build error message
        item = form.instance
        item_name = str(item.manufacturer) + " " + str(item.itemType)
        parent_item = str(item.item.manufacturer) + " " + str(item.item.itemType)
        message = "Couldn't attach " + item_name + " to " + parent_item + ". Invalid Form Data."
        return render_to_response('ajax_move_item_confirm.html', locals())

    def form_valid(self, form):
        message = ""
        item = form.instance
        item_name = str(item.manufacturer) + " " + str(item.itemType)
        parent_item = str(item.item.manufacturer) + " " + str(item.item.itemType)
        if form.has_changed():
            form.save(user=self.request.user)
            #build confirm message
            alert_type = "success"
            message = item_name + " attached to " + parent_item
        else:
            alert_type = "warning"
            message = item_name + " is already attached to " + parent_item
        return render_to_response('ajax_move_item_confirm.html', locals())

class AjaxDetachItem(AjaxMoveItem):
    form_class = AttachItemForm
    success_url = "/"

    def form_invalid(self, form):
        alert_type = "danger"
        #build error message
        item = form.instance
        item_name = str(item.manufacturer) + " " + str(item.itemType)
        parent_item = str(item.item.manufacturer) + " " + str(item.item.itemType)
        message = "Couldn't detach " + item_name + " from " + parent_item + ". Invalid Form Data."
        return render_to_response('ajax_move_item_confirm.html', locals())

    def form_valid(self, form):
        message = ""
        item = form.instance
        item_name = str(item.manufacturer) + " " + str(item.itemType)
        old_item = Item.objects.get(id=item.id)
        parent_item = Item.objects.get(id=old_item.item.id)
        parent_name = str(parent_item.manufacturer) + " " + str(parent_item.itemType)
        if form.has_changed():
            form.save(user=self.request.user)
            #build confirm message
            alert_type = "success"
            message = item_name + " detached from " + parent_name
        else:
            alert_type = "warning"
            message = item_name + " was not already attached to " + parent_name
        return render_to_response('ajax_move_item_confirm.html', locals())

class AjaxArchiveItem(LoginRequiredMixin, FormView):
    form_class = ArchiveItemForm
    success_url = "/"

    def get_form(self, form_class=None):
        item = get_object_or_404(Item, id=self.args[0])
        return form_class(self.request.POST, instance=item)
        
    def form_invalid(self, form):
        alert_type = "danger"
        #build error message
        item = form.instance
        itemType = str(item.itemType)
        message = "Couldn't archive " + itemType + ". Invalid Form Data."
        return render_to_response('ajax_move_item_confirm.html', locals())

    def form_valid(self, form):
        message = ""
        item = form.instance
        item_name = str(item.manufacturer) + " " + str(item.itemType)
        if form.has_changed():
            form.save(user=self.request.user)
            #build confirm message
            alert_type = "success"
            message = item_name + " Archived."
        else:
            alert_type = "warning"
            message = item_name + " was already archived."
        return render_to_response('ajax_move_item_confirm.html', locals())

