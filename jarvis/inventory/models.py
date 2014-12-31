from django.db import models
from djangotoolbox.fields import EmbeddedModelField, ListField, DictField, SetField

# Create your models here.

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

  #returns a list of all items associated with this room
  def getAllItems(self):
  	 return self.item_set.all()
	 
  def __str__(self):
  	 return self.number

#Stores all information about a single item
class Item(models.Model):
  #static fields
  itemType = models.CharField(max_length=50)
  manufacturer = models.CharField(max_length=50)
  model = models.CharField(max_length=50)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  room_id = models.ForeignKey(Room, null=True)

  #dyn fields
  attributes = DictField()
  ipInterfaces = ListField(EmbeddedModelField('IPInterface'))
  subitems = ListField(EmbeddedModelField('Item'))

  def save(self):
  	 #get old version of document
	 old = Item.objects.filter(pk=self.pk)[0]
	 print(old)
	 super(Item, self).save()

  def __str__(self):
  	 return self.itemType + " " + self.manufacturer + " " + self.model

class IPInterface(models.Model):
  ipAddress = models.CharField(max_length=50, unique=True)
  macAddress = models.CharField(max_length=20, unique=True, null=True)
  

#Each instance of ItemRevision stores all revision history for a single
# instance of the Item class.
class ItemRevision(models.Model):
  itemId = models.ForeignKey(Item)
  changes = DictField()


