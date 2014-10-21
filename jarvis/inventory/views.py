from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.generic.base import View

# Create your views here.
class Home(View):
  def get(self, request):
	 return render_to_response('dashboard.html', locals())

class DBTest(View):
  def get(self, request):
	 return render_to_response('dbtest.html', locals())
