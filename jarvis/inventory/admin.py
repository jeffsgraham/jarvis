from django.contrib import admin
from models import *

#exclude list field from admin interface
class ItemModelAdmin(admin.ModelAdmin):
    exclude = ('indicativeAttributes',)


admin.site.register(Type)
admin.site.register(Model, ItemModelAdmin)
admin.site.register(Manufacturer)
admin.site.register(IPRange)
admin.site.register(Building)
admin.site.register(Room)
