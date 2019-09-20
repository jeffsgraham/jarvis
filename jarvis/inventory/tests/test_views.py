from django.test import TestCase
from django.contrib.auth.models import User
from inventory.models import *

class AbstractViewTests():
    base_url = "/"
    suffix_url = ""
    username = "test"
    password = "password"
    context_keys = []

    def setUp(self):
        User.objects.create_user(username=self.username, password=self.password)

class AbstractViewGetTests(AbstractViewTests):
    def test_login_required(self):
        resp = self.client.get(self.base_url, follow=True)
        self.assertEqual(len(resp.redirect_chain), 1) #exactly one redirect
        #redirect is to login page
        self.assertEqual(resp.redirect_chain[0][0],"/accounts/login/?next=" + self.base_url)
        self.assertEqual(resp.redirect_chain[0][1], 302) #http code is 302

    def test_resp_code(self):
        self.client.login(username=self.username, password=self.password)
        resp = self.client.get(self.base_url)
        self.assertEqual(resp.status_code, 200)

    def test_context(self):
        self.client.login(username=self.username, password=self.password)
        resp = self.client.get(self.base_url)
        #context contains required fields
        for key in self.context_keys:
            self.assertTrue(key in resp.context)


class AbstractViewPostTests(AbstractViewTests):
    def test_post_login_required(self):
        resp = self.client.post(self.base_url, follow=True)
        self.assertEqual(len(resp.redirect_chain), 1) #exactly one redirect
        #redirect is to login page
        self.assertEqual(resp.redirect_chain[0][0], "/accounts/login/?next=" + self.base_url)
        self.assertEqual(resp.redirect_chain[0][1], 302) #http code is 302
        
    

class MainListTestCase(AbstractViewGetTests, TestCase):
    base_url = "/"
    context_keys = ['rooms', 'buildings']

class AjaxMainListTextCase(AbstractViewGetTests, TestCase):
    base_url = "/inventory/item/all/"
    context_keys = ['items', 'pagetitle', 'content_url']


class AjaxRoomViewTestCase(AbstractViewGetTests, TestCase):
    base_url = "/inventory/room/"
    suffix_url = "/item/all/"
    context_keys = ['room', 'items', 'pagetitle', 'content_url']

    def setUp(self):
        super(AjaxRoomViewTestCase, self).setUp()
        building = Building.objects.create(name="Alderwood", abbrev="ALD")
        room = Room.objects.create(number="101", building=building)
        self.base_url += str(room.pk) + self.suffix_url

class AjaxEditItemTestCase(AbstractViewGetTests, TestCase):
    base_url = "/inventory/item/"
    suffix_url = "/edit/"
    context_keys = ['item', 'title', 'submit_url']
    
    def setUp(self):
        super(AjaxEditItemTestCase, self).setUp()
        compType = Type.objects.get_or_create(name="Computer")[0]
        hpManuf = Manufacturer.objects.get_or_create(name="HP")[0]
        dcModel = Model.objects.get_or_create(name="DC8300")[0]
        item = Item.objects.create(itemType=compType, manufacturer=hpManuf, model=dcModel)
        self.base_url += str(item.pk) + self.suffix_url

"""
    def get_context_data(self, **kwargs):
        context = super(AjaxEditItem, self).get_context_data(**kwargs)
        context['item'] = get_object_or_404(Item, id=self.args[0])
        context['title'] = "Edit Item Form"
        context['submit_url'] = "/ajax_edit_item/" + context['item'].pk + "/"
        return context

    def get_form(self, form_class=None):
        item = get_object_or_404(Item, id=self.args[0])
        return ItemForm(self.request.POST, instance=item)

    def form_invalid(self, form):
        return HttpResponse("Invalid Form Data", content_type="text/plain")

    def form_valid(self, form):
        form.save()
        return HttpResponse("Saved", content_type="text/plain")
"""
class AjaxAddItemTestCase(AbstractViewGetTests, TestCase):
    base_url = "/inventory/item/add/"
    context_keys = ['title', 'submit_url']

class AjaxAddItemToRoomTestCase(AbstractViewGetTests, AbstractViewPostTests, TestCase):
    base_url = "/inventory/room/"
    suffix_url = "/item/add/"
    context_keys = ['room', 'title', 'submit_url']

    def setUp(self):
        super(AjaxAddItemToRoomTestCase, self).setUp()
        building = Building.objects.create(name="Alderwood", abbrev="ALD")
        room = Room.objects.create(number="101", building=building)
        self.base_url += str(room.pk) + self.suffix_url

"""
class AjaxAddItem(AjaxEditItem):

    def get_context_data(self, **kwargs):
        context = super(AjaxEditItem, self).get_context_data(**kwargs) #grandparent's method
        if(len(self.args) >= 1): #if room id has been passed
            context['room'] = get_object_or_404(Room, id=self.args[0])
        room_id = (context['room'].pk + "/") if ('room' in context) else ("")
        context['title'] = "Add Item Form"
        context['submit_url'] = "/ajax_add_item/" + room_id
        return context

    def get_form(self, form_class=None):
        return ItemForm(self.request.POST)
"""
