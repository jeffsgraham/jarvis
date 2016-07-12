from django.contrib import admin
from models import *

#exclude list field from admin interface
class ItemModelAdmin(admin.ModelAdmin):
    exclude = ('partNumbers',)

class ItemAdmin(admin.ModelAdmin):
    exclude = ('attributes','uptime',)
    list_display = ('itemType', 'manufacturer', 'model', 'room', 'getSerial', 'getIPAddress')

    def getSerial(self, item):
        return item.attributes.get('Serial', '')
    getSerial.short_description = 'Serial'
    
    def getIPAddress(self, item):
        return item.attributes.get('IP Address', '')
    getIPAddress.short_description = 'IP Address'

admin.site.register(Type)
admin.site.register(Model, ItemModelAdmin)
admin.site.register(Manufacturer)
admin.site.register(Attribute)
admin.site.register(IPRange)
admin.site.register(Building)
admin.site.register(Room)
admin.site.register(Item, ItemAdmin)
