from rest_framework import serializers
from inventory.models import *
from django.contrib.auth.models import User

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']

class RoomSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Room
        fields = ['url', 'number', 'building', 'schedule_url']

class BuildingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Building
        fields = ['url', 'name', 'abbrev']

class ManufacturerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ['url', 'name']

class TypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Type
        fields = ['url', 'name']

class ModelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Model
        fields = ['url', 'name', 'manufacturer', 'itemType']

class ItemSerializer(serializers.HyperlinkedModelSerializer):
    attributes = serializers.DictField()

    def validate_attributes(self, value):
        #validate type
        if type(value) != dict:
            raise serializers.ValidationError("item attributes must be of type <dict>")
        
        #validate SID
        if "State ID" in value:
            state_id = value['State ID']
            if type(state_id) != str:
                raise serializers.ValidationError("Error: State ID attribute must be of type string, received " + str(type(state_id)))
            if len(state_id) != 7:
                raise serializers.ValidationError("Error: State ID attribute must be exactly 7 characters, received " + str(len(state_id)))
            if state_id[0] != 'B':
                raise serializers.ValidationError("Error: State ID attribute must begin with 'B', received " + str(state_id[0]))
        

        #TODO: add model validation rules for serial numbers
        return value
    
    class Meta:
        model = Item
        fields = ['url', 'manufacturer', 'itemType', 'model', 'room', 'attributes', 'created']

class ItemRevisionSerializer(serializers.HyperlinkedModelSerializer):
    changes = serializers.DictField()
    class Meta:
        model = ItemRevision
        fields = ['url', 'item', 'revised', 'user', 'changes']

class ItemSuggestionSerializer(serializers.Serializer):
    """custom serializer for item suggestions base on serial number"""
    model = serializers.CharField()
    manufacturer = serializers.CharField()
    itemType = serializers.CharField()
    confidence = serializers.FloatField()