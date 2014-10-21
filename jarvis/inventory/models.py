from django.db import models
from djangotoolbox.fields import ListField

# Create your models here.

class Item(models.Model):
    serial = models.CharField(max_length=50)
    sid = models.CharField(max_length=10)
