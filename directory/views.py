from django.shortcuts import render_to_response, redirect
from directory.models import *
from directory.forms import *
from django.core.context_processors import csrf
from django.forms.formsets import formset_factory
from services.object import LBEObjectInstanceHelper
from django.contrib import messages
from django.template import RequestContext
from services.backend import BackendDao

def index(request):
	backend = BackendDao()
	objects = backend.searchObjects(LBEObjectTemplate.objects.get(name='employee'))
	return render_to_response('directory/default/index.html', { 'objects': objects }, context_instance=RequestContext(request))

# Create an instance of LBEObjectInstance from LBEObject definition. Save it into MongoDB with status AWAITING_SYNC
def addObjectInstance(request, lbeObject_id = None):
	form = None
	if (request.method == 'POST'):
		form = LBEObjectInstanceForm(LBEObjectTemplate.objects.get(id = lbeObject_id), request.POST)
		if form.is_valid():
			helper = LBEObjectInstanceHelper(LBEObjectTemplate.objects.get(id = lbeObject_id))
			# try:
			helper.createFromDict(request.POST)
			# except BaseException as e:
				# print e
				# messages.add_message(request, messages.ERROR, 'An error occured while creating the object.')
			return render_to_response('directory/default/object/add.html', { 'form': form, 'lbeObjectId': lbeObject_id }, context_instance=RequestContext(request))
		else:
			return render_to_response('directory/default/object/add.html', { 'form': form, 'lbeObjectId': lbeObject_id }, context_instance=RequestContext(request))
		print request.POST
	else:
		if lbeObject_id == None:
			# TODO: Redirect to a form to choose which object to add
			print 'error'
	form = LBEObjectInstanceForm(LBEObjectTemplate.objects.get(id = lbeObject_id))
	return render_to_response('directory/default/object/add.html', { 'form': form, 'lbeObjectId': lbeObject_id }, context_instance=RequestContext(request))
