from django.forms import ModelForm, TextInput, CharField
from models import *



#have to maintain custom for for Items as DictField doesn't work with automagic form generation
class ItemForm(ModelForm):
    def is_valid(self):
        #add code table entries if not present
        Type.objects.get_or_create(name=self.data['itemType'])
        Manufacturer.objects.get_or_create(name=self.data['manufacturer'])
        Model.objects.get_or_create(name=self.data['model'])
        return super(ItemForm, self).is_valid()

    class Meta:
        model = Item
        exclude = ('attributes', 'active', 'created', 'item', 'uptime')
        widgets = {
            'itemType': TextInput(),
            'manufacturer': TextInput(),
            'model': TextInput(),
        }



class ItemForm2(ModelForm):
    class Meta:
        model = Item
        exclude = ('active', 'created', 'item', 'uptime')
        widgets = {
            'itemType': TextInput(),
            'manufacturer': TextInput(),
            'model': TextInput(),
        }

class MoveItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ('room','item')


class AttachItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ('item',)


class DetachItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ('item',)
