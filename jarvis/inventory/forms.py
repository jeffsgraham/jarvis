from django.forms import ModelForm
from models import *

#have to maintain custom for for Items as DictField doesn't work with automagic form generation
class ItemForm(ModelForm):
    class Meta:
        model = Item
        exclude = ('attributes', 'active', 'created', 'item')
