from django.db import models
from djangotoolbox.fields import EmbeddedModelField, ListField, DictField, SetField

# Create your models here.

class Item(models.Model):
  #static fields
  manufacturer = models.CharField(max_length=50)
  model = models.CharField(max_length=50)
  serial = models.CharField(null=True, max_length=50)
  stateId = models.CharField(null=True, max_length=10)
  itemType = models.CharField(max_length=50)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  #dyn fields
  attributes = DictField()
  ipInterfaces = SetField(EmbeddedModelField('IpInterface'))
  revisions = SetField(EmbeddedModelField('ItemRevision'))


class IPInterface(models.Model):
  ipAddress = models.CharField(max_length=50, unique=True)
  macAddress = models.CharField(max_length=20, unique=True, null=True)
  
class ItemRevision(models.Model):
  revised = models.DateTimeField(auto_now_add=True)
  changes = DictField()
