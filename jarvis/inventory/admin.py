from django.contrib import admin
from django import forms
from inventory.models import *

class CascadeNameChangeForm(forms.ModelForm):
    #override save to update related objects when name changes
    def save(self, *args, **kwargs):
        #check that this is an update operation
        if self.instance.pk is not None and 'name' in self.changed_data:
            #get old version of object from database
            old = type(self.instance).objects.filter(pk=self.instance.pk)[0]
            #call instance's cascade_name_change() to update related objects
            self.instance.cascade_name_change(old)
        #save the pending changes and return
        return super(CascadeNameChangeForm, self).save(*args, **kwargs)

class ItemModelAdminForm(CascadeNameChangeForm):
    class Meta:
        model = Model
        exclude = ['partNumbers']

class ItemModelAdmin(admin.ModelAdmin):
    form = ItemModelAdminForm
    #exclude list field from admin interface
    exclude = ('partNumbers',)

class CascadeNameChangeAdmin(admin.ModelAdmin):
    form = CascadeNameChangeForm

class ItemAdmin(admin.ModelAdmin):
    exclude = ('attributes',)
    list_display = ('itemType', 'manufacturer', 'model', 'room', 'getSerial', 'getIPAddress')

    def getSerial(self, item):
        return item.attributes.get('Serial', '')
    getSerial.short_description = 'Serial'
    
    def getIPAddress(self, item):
        return item.attributes.get('IP Address', '')
    getIPAddress.short_description = 'IP Address'

admin.site.register(Type, CascadeNameChangeAdmin)
admin.site.register(Model, ItemModelAdmin)
admin.site.register(Manufacturer, CascadeNameChangeAdmin)
admin.site.register(Attribute)
admin.site.register(Building)
admin.site.register(Room)
admin.site.register(Item, ItemAdmin)