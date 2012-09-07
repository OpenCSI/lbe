from django.shortcuts import render_to_response, redirect
from directory.models import *
from django.http import HttpResponse, HttpResponseRedirect

def index(request):
	return render_to_response('manage/index.html')
