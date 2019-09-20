from django.shortcuts import get_object_or_404, render_to_response
#from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic.base import View
from django.views.generic import FormView, TemplateView
#from django.contrib.auth.views import login as django_login
from rest_framework import viewsets, permissions
from rest_framework.generics import ListAPIView
from rest_framework.decorators import action
from rest_framework.response import Response
from inventory.serializers import UserSerializer, RoomSerializer, BuildingSerializer, ManufacturerSerializer, TypeSerializer, ModelSerializer, ItemSerializer, ItemRevisionSerializer, ItemSuggestionSerializer
from inventory.models import Building, Room, Model, Manufacturer, Type, Item, Attribute, ItemRevision
from inventory.forms import ItemForm2, MoveItemForm, AttachItemForm, ArchiveItemForm


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
        #sort results by input
        item_fields = [ f.name for f in Item._meta.fields ]
        order_list = [] #list of fields to order_by
        sort_fields = request.GET.get('sort_by','')
        for rule in sort_fields.split(','):
            #only use sort rules on fields that exist
            if rule.replace('-','') in item_fields:
                order_list.append(rule)
        items = Item.objects.filter(active=True, item=None, room=None).order_by(*order_list)
        pagetitle = "Warehouse"
        content_url = request.META['PATH_INFO']
        return render_to_response('ajax_item_list.html', locals())


class AjaxSearchItems(LoginRequiredMixin, View):
    """AJAX view that lists all active items that match the given search terms."""
    def get(self, request, *args):
        search_term = self.args[0]
        # build order list to use in sorting results. 
        # the sort_by querystring is returned when a user has selected
        #  a column heading for sorting in the search results
        order_list = request.GET.get('sort_by','').split(',')
        sort_order = [
            (sort_field[1:], -1) if sort_field[0] == '-' else (sort_field, 1)
            for sort_field in order_list
            if sort_field
        ]
        
        # search the database
        items = Item.search(self.args[0], sort_order)
        
        pagetitle = "Results for " + self.args[0]
        content_url = request.META['PATH_INFO']
        disable_add = True
        show_location = True
        return render_to_response('ajax_item_list.html', locals())

class AjaxItemDetail(LoginRequiredMixin, View):
    """AJAX view that shows item details."""
    def get(self, request, *args):
        item = get_object_or_404(Item, pk=self.args[0])
        revisions = item.itemrevision_set.order_by("-revised")
        content_url = request.META['PATH_INFO']
        return render_to_response('ajax_detail_view.html', locals())

class AjaxRoomView(LoginRequiredMixin, View):
    """AJAX View for room info requests. Lists all items in requested room."""
    def get(self, request, room_id, *args):
        room = get_object_or_404(Room, pk=room_id)#self.args[0])
        #sort results by input
        item_fields = [ f.name for f in Item._meta.fields ]
        order_list = [] #list of fields to order_by
        sort_fields = request.GET.get('sort_by','')
        for rule in sort_fields.split(','):
            #only use sort rules on fields that exist
            if rule.replace('-','') in item_fields:
                order_list.append(rule)
        items = room.item_set.filter(active=True, item=None).order_by(*order_list)

        pagetitle = room.building.abbrev + " " + str(room.number)

        content_url = request.META['PATH_INFO']
        return render_to_response('ajax_item_list.html', locals())

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
        context['itemTypes'] = Type.objects.all().order_by("name")
        context['manufacturers'] = Manufacturer.objects.all().order_by("name")
        context['models'] = Model.objects.all().order_by("name")
        context['attrSuggestions'] = Attribute.objects.all().order_by("name")

        context['item'] = get_object_or_404(Item, pk=self.args[0])
        context['title'] = "Edit Item Form"
        context['submit_url'] = "/inventory/item/" + str(context['item'].pk) + "/edit/"
        return context

    def get_form(self, form_class=None):
        item = get_object_or_404(Item, pk=self.args[0])
        if not form_class:
            form_class = self.form_class
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

        context['itemTypes'] = Type.objects.all().order_by("name")
        context['manufacturers'] = Manufacturer.objects.all().order_by("name")
        context['models'] = Model.objects.all().order_by("name")

        if(len(self.args) >= 1): #if room id has been passed
            context['room'] = get_object_or_404(Room, pk=self.args[0])
        room_id = ("room/" + str(context['room'].pk) + "/") if ('room' in context) else ("")
        context['title'] = "Add Item Form"
        context['submit_url'] = "/inventory/" + room_id + "item/add/"
        return context

    def get_form(self, form_class=None):
        if not form_class:
            form_class = self.form_class
        return form_class(self.request.POST)

class AjaxMoveItem(LoginRequiredMixin, FormView):
    form_class = MoveItemForm
    success_url = "/"

    def get_form(self, form_class=None):
        item = get_object_or_404(Item, pk=self.args[0])
        if not form_class:
            form_class = self.form_class
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
        room_name = str(item.room or "Warehouse") #default to warehouse if room=None
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
        old_item = Item.objects.get(pk=item.pk)
        parent_item = Item.objects.get(pk=old_item.item.pk)
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
        item = get_object_or_404(Item, pk=self.args[0])
        if not form_class:
            form_class = self.form_class
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



# API Views
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = BuildingSerializer

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = RoomSerializer

class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ManufacturerSerializer

class ModelViewSet(viewsets.ModelViewSet):
    queryset = Model.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ModelSerializer

class TypeViewSet(viewsets.ModelViewSet):
    queryset = Type.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TypeSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ItemSerializer

    def perform_update(self, serializer, *args, **kwargs):
        """Override perform_update to add a "blame" user which will be tagged
        to any ItemRevisions created as a consequence of this update.
        TODO: This might be better accomplished with serializer attributes: 
         https://www.django-rest-framework.org/api-guide/serializers/#passing-additional-attributes-to-save
        """
        # monkey patch blame user directly to model instance
        # this will be used in models.Item.save_with_revisions(...)
        serializer.instance.blame = self.request.user
        super().perform_update(serializer, *args, **kwargs)

class ItemSuggestion(ListAPIView):
    serializer_class = ItemSuggestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        serial = self.request.query_params.get('serial', 'MXL0331234')
        if not serial or type(serial) != str:
            return Response(None)
        return Item.guessFromSerial2(serial)

class ItemRevisionViewSet(viewsets.ReadOnlyModelViewSet):
    """Revisions should never be created manually, so this is read only."""
    queryset = ItemRevision.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ItemRevisionSerializer