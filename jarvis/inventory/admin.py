from django.contrib import admin
from models import Item, Type, Model, Manufacturer

# Register your models here.
admin.site.register(Item)
admin.site.register(Type)
admin.site.register(Model)
admin.site.register(Manufacturer)
