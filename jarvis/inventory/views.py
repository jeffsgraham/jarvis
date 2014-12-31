from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.generic.base import View
from django.views.generic import ListView

from models import *

# Create your views here.
class Home(View):
  def get(self, request):
	 return render_to_response('Template.htm', locals())

class DBTest(View):
  def get(self, request):
	 return render_to_response('dbtest.html', locals())

class RoomItemList(ListView):
  model = Item
  
  def get_queryset(self):
  	 self.room_id = get_object_or_404(Room, pk=self.args[0])
  	 return Item.objects.filter(room_id=self.room_id)


	 
