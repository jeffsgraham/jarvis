from django.db import models
from django.conf import settings
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
  room = models.ForeignKey('Room', null=True)
  item = models.ForeignKey('self', null=True)

  #dyn fields
  attributes = DictField()
  ipInterfaces = ListField(EmbeddedModelField('IPInterface'))

  def save_with_revisions(self, currentUser):
  	 #get old version of document
	 old = Item.objects.filter(pk=self.pk)[0]
	 print(old)
  
	 #check for any changes
	 if(old != self or old.attributes != self.attributes):

	 	#create ItemRevision object
	 	revision = ItemRevision.objects.create(item=self, user=currentUser)
		print('revision created')
		if(old.itemType != self.itemType):
		  #store old itemType
		  revision.changes['itemType'] = old.itemType

		if(old.manufacturer != self.manufacturer):
		  #store old manufacturer
		  revision.changes['manufacturer'] = old.manufacturer

		if(old.model != self.model):
		  #store old model
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

		revision.save()

	 super(Item, self).save()

  

  def __str__(self):
  	 return self.itemType + " " + self.manufacturer + " " + self.model

class IPInterface(models.Model):
  ipAddress = models.CharField(max_length=50, unique=True)
  macAddress = models.CharField(max_length=20, unique=True, null=True)
  
#Each instance represents changes to a single item at a given time
class ItemRevision(models.Model):
  item = models.ForeignKey(Item)
  revised = models.DateTimeField(auto_now_add=True)
  user = models.ForeignKey(settings.AUTH_USER_MODEL)
  changes = DictField()

  #reverts an item back to the previous state described by this ItemRevision 
  # instance. This should only be called by the Item.revertChanges() method,
  # as all ItemRevisions done since this ItemRevision must be reverted before
  # this one is reverted.
  def revert(self):
	 for key, value in changes.iteritems():
		if key == 'itemType':
		  self.item.itemType = value
		elif key == 'manufacturer':
		  self.item.manufacturer = value
		elif key == 'model':
		  self.item.model = value
		elif key == 'room':
		  self.item.room = value
		elif key == 'item':
		  self.item.item = value
		elif value is None:
		  del self.item.attribute[key]
		else:
		  self.item.attributes[key] = value
		  
	 

  def __str__(self):
  	 return "Item: " + self.item + " Revised: " + self.revised + " by: " + self.user

