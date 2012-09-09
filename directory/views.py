from django.shortcuts import render_to_response, redirect
from directory.models import *
from django.core.context_processors import csrf

from django.contrib import messages
from django.template import RequestContext
from services.backend import BackendDao

def index(request):
	backend = BackendDao()
	objects = backend.searchObject(LBEObject.objects.get(name='employee'))
	messages.add_message(request, messages.DEBUG, 'test')
	return render_to_response('directory/default/index.html', None, context_instance=RequestContext(request))