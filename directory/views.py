from django.shortcuts import render_to_response, redirect
from directory.models import *
from directory.forms import *
from django.core.context_processors import csrf

from django.contrib import messages
from django.template import RequestContext
from services.backend import BackendDao

def index(request):
	backend = BackendDao()
	objects = backend.searchObjects(LBEObject.objects.get(name='employee'))
	return render_to_response('directory/default/index.html', { 'objects': objects }, context_instance=RequestContext(request))

# Create an instance of LBEObjectInstance from LBEObject definition. Save it into MongoDB with status AWAITING_SYNC
def addObjectInstance(request, lbeObject_id):
	if (request.method == 'POST'):
		print request.POST
		return render_to_response('directory/default/object/add.html', { 'lbeObject': LBEObject.objects.get(id=lbeObject_id), }, context_instance=RequestContext(request))
	else:
		pass
	return render_to_response('directory/default/object/add.html', { 'lbeObject': LBEObject.objects.get(id=lbeObject_id), }, context_instance=RequestContext(request))
