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


class BaseItemForm(ModelForm):
    class Meta:
        model = Item
        fields = {}

    def save(self, commit=True, user=None, *args, **kwargs):
        if commit == True:
            #create revision
            item = self.save(commit=False, *args, **kwargs)
            item.save_with_revisions(user=user, *args, **kwargs)
        else:
            return super(BaseItemForm, self).save(commit=commit, *args, **kwargs)


class ItemForm2(BaseItemForm):
    class Meta:
        model = Item
        exclude = ('active', 'created', 'item', 'uptime')
        widgets = {
            'itemType': TextInput(),
            'manufacturer': TextInput(),
            'model': TextInput(),
        }
  
        

class MoveItemForm(BaseItemForm):
    class Meta:
        model = Item
        fields = ('room','item')

    def save(self, commit=True, user=None, *args, **kwargs):
        retVal = super(MoveItemForm, self).save(commit=commit, *args, **kwargs)
        if commit == True:
            #move subitems
            for item in self.instance.subItem.all():
                item.room = self.instance.room
                item.save(user=user)
        return retVal

class AttachItemForm(BaseItemForm):
    class Meta:
        model = Item
        fields = ('item',)

class DetachItemForm(BaseItemForm):
    class Meta:
        model = Item
        fields = ('item',)

class ArchiveItemForm(BaseItemForm):
    class Meta:
        model = Item
        fields = ('active',)
