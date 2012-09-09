from django.shortcuts import render_to_response, redirect
from directory.models import *
from django.core.context_processors import csrf

from django.contrib import messages
from django.template import RequestContext
from services.backend import BackendDao

def index(request):
	backend = BackendDao()
	objects = backend.searchObjects(LBEObject.objects.get(name='employee'))
	return render_to_response('directory/default/index.html', { 'objects': objects }, context_instance=RequestContext(request))