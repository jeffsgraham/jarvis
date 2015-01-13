from django.db import models
from django.conf import settings
from djangotoolbox.fields import EmbeddedModelField, ListField, DictField, SetField
from copy import copy, deepcopy


#stores relevant information about buildings
class Building(models.Model):
    name = models.CharField(max_length=50)
    abbrev = models.CharField(max_length=3)
    rooms = ListField(EmbeddedModelField('Room'))
    
    def add_room(self, room):
        self.rooms.append(room)
        self.rooms.sort()
  
    def __str__(self):
        return self.name + " (" + self.abbrev + ")"

#Stores relevant information about rooms
class Room(models.Model):
    number = models.CharField(max_length=10)

    def __str__(self):
        return self.number

#Stores all information about a single item
class Item(models.Model):
    #static fields
    itemType = models.CharField(max_length=50)
    manufacturer = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey('Room', null=True)
    item = models.ForeignKey('self', null=True, related_name="subItem")

    #dyn fields
    attributes = DictField()

    def save_with_revisions(self, currentUser=None):
        #get old version of document
	old = Item.objects.filter(pk=self.pk)
        
        #make sure there is an old copy
        if not len(old) == 0:
            old = old[0] #get Item instance from list
  
            #check for any changes
            if(old != self or old.attributes != self.attributes or \
                    old.item != self.item or old.room != self.room):

                #create ItemRevision object
                revision = ItemRevision.objects.create(item=self, user=currentUser)
                
                #store old itemType
                if(old.itemType != self.itemType):
                    revision.changes['itemType'] = old.itemType

                #store old manufacturer
                if(old.manufacturer != self.manufacturer):
                    revision.changes['manufacturer'] = old.manufacturer

                #store old model
                if(old.model != self.model):
                    revision.changes['model'] = old.model

                #store old attributes that have been removed or changed
                for key, value in old.attributes.iteritems():
                    if not (key in self.attributes and self.attributes[key] == value):
                        revision.changes[key] = value

                #store newly aquired attributes as null
                for key, value in self.attributes.iteritems():
                    if not key in old.attributes:
                        revision.changes[key] = None

                #store room
                if(old.room != self.room):
                    revision.changes['room'] = old.room

                #store item attachment
                if(old.item != self.item):
                    revision.changes['item'] = old.item
                
                #save new revision object to DB
                revision.save()

        #save Item instance
        self.save()

  
    #reverts an item back to the previous state described by the given
    # ItemRevision instance.
    def revert(self, revision):
        #get revision history sorted by date
        revisions = ItemRevision.objects.filter(item=self).order_by("-revised")
        for rev in revisions:

            #revert to this revision
            for key, value in rev.changes.iteritems():
                #handle static fields
                if key == 'itemType':
                    self.itemType = value
                elif key == 'manufacturer':
                    self.manufacturer = value
                elif key == 'model':
                    self.model = value
                elif key == 'room':
                    self.room = value
                elif key == 'item':
                    self.item = value
                elif value is None: #remove new attributes
                    del self.attributes[key]
                else: #revert old attributes
                    self.attributes[key] = value

            #delete revision from DB after reverting
            rev.delete()

            #stop reverting to revisions if this is the last one
            if rev == revision:
                break
        #save reverted state
        self.save()

    #overload __eq__() to only compare important fields
    def __eq__(self, compare):
        #check that object type is the same
        if not isinstance(compare, Item):
            return False
        #check all pertenint variables
        if compare.itemType == self.itemType and \
            compare.manufacturer == self.manufacturer and \
            compare.model == self.model and \
            compare.attributes == self.attributes and \
            compare.item == self.item and compare.room == self.room:
            return True
        else:
            return False

    def __str__(self):
        return str(self.itemType) + " " + str(self.manufacturer) + " " + str(self.model)

#Each instance represents changes to a single item at a given time
class ItemRevision(models.Model):
    item = models.ForeignKey(Item)
    revised = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    changes = DictField() 

    def __eq__(self, compare):
        if not isinstance(compare, ItemRevision):
            return False
        if self.revised == compare.revised and self.user == compare.user and \
            self.item.id == compare.item.id and self.changes == compare.changes:
            return True
        else:
            return False

    def __str__(self):
        return "Item: [" + str(self.item) + "], Revised: [" + str(self.revised) + \
        "], by: [" + str(self.user) + "]"

