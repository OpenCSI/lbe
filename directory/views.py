from django.shortcuts import render_to_response, redirect
from directory.models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf

def index(requestContext):
	return render_to_response('index.html')