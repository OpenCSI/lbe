from django.shortcuts import render_to_response, redirect
from directory.models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext

def addObject(request):
	if request.method == 'POST':
		form = LBEObjectForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('/config/object/list')
	else:
		form = LBEObjectForm()
	return render_to_response('config/object/create.html', { 'objectForm': form }, context_instance=RequestContext(request))

def listObjects(request):
	return render_to_response('config/object/list.html', { 'objects': LBEObject.objects.all() })

def modifyObject(request, obj_id = None):
	if request.method == 'POST':
		form = LBEObjectForm(request.POST, instance = LBEObject.objects.get(id = obj_id))
		if form.is_valid():
			form.save()
			return redirect('/config/object/modify/' + obj_id)
		else:
			# Send errors in the console for the moment
			print form.errors
	else:
		if (obj_id == None):
			return render_to_response('config/object/list.html', { 'objects': LBEObject.objects.all() })
	lbeObject = LBEObject.objects.get(id = obj_id)
	objectForm = LBEObjectForm(instance = lbeObject)
	attForm = LBEAttributeInstanceForm()
	instances = LBEAttributeInstance.objects.filter(lbeObject = lbeObject)
	return render_to_response('config/object/modify.html', { 'attributeInstances': instances, 'lbeObject': lbeObject, 'objectForm': objectForm, 'attributeForm': attForm},\
		context_instance=RequestContext(request))

def addObjectAttribute(request, obj_id):
	if request.method == 'POST':
		form = LBEAttributeInstanceForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('/config/object/modify/' + obj_id)
		else:
			print form.errors
	return redirect('/config/object/modify/' + obj_id)
