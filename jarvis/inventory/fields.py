from django.forms import ModelForm, TextInput, CharField
from django.db import models
import json

class DictFormField(CharField):

    def to_python(self, value):
        """
            Returns a python dictionary object
            
            Note that json.loads() will not fail if given non-unique keys
            Instead it will decode only the last key-value pair of any
            given non-unique key set.

        """

        if not value:
            return {}
        #TODO: Handle possible errors
        value = json.loads(value)
        return value
    
    def clean(self, value):
        """Removes empty string keys from dictionary"""
        value = super(DictFormField, self).clean(value)
        value.pop("", None) #remove empty string key if found
        return value

