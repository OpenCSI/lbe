from django.shortcuts import render_to_response, redirect
from directory.models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib import messages
from django.template import RequestContext


def index(request):
	messages.add_message(request, messages.INFO, 'Welcome')
	return render_to_response('directory/default/index.html', None, context_instance=RequestContext(request))