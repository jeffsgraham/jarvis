from django.test import TestCase
from models import *

# Create your tests here.

class ItemTestCase(TestCase):
  def setUp(self):
	 Item.objects.create(manufacturer='Extron', model='DVS304', itemType='Video Scaler')
