from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.template import RequestContext
from directory.models import *
from directory.forms import *
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse

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

def modifyObject(request, obj_id = None, instance_id = None):
	objectForm = None
	lbeObject = LBEObject.objects.get(id = obj_id)
	if request.method == 'POST':
		objectForm = LBEObjectForm(request.POST, instance = LBEObject.objects.get(id = obj_id))
		if objectForm.is_valid():
			objectForm.save()
			messages.add_message(request, messages.INFO, 'Object saved')
			return redirect('/config/object/modify/' + obj_id)
		else:
			messages.add_message(request, messages.ERROR, 'Error while saving object')
	else:
		if (obj_id == None):
			messages.add_message(request, messages.INFO, 'object id is missing')
			return render_to_response('config/object/list.html', { 'objects': LBEObject.objects.all() })
		else:
			objectForm = LBEObjectForm(instance= lbeObject)
	attForm = LBEAttributeInstanceForm()
	instances = LBEAttributeInstance.objects.filter(lbeObject = lbeObject)
	# which attribute have ajax request:
	ajaxAttribute = 'rdnAttribute'
	defaultValue = lbeObject.rdnAttribute.name
	# Ajax function to call (js):
	ajaxFunction = 'selectFrom(\'' + reverse('config.views.showAttributeAJAX') +'\',\''+ajaxAttribute+'\');'
	return render_to_response('config/object/modify.html', { 'attributeInstances': instances, 'lbeObject': lbeObject, 'objectForm': objectForm, 'attributeForm': attForm,'ajaxAttribute':ajaxAttribute,'ajaxFunction':ajaxFunction,'defaultValue':defaultValue},\
		context_instance=RequestContext(request))

def modifyObjectAJAX(request,obj_id = None):
	if request.is_ajax():
		lbeObject = LBEObject.objects.get(id = obj_id)
		if (obj_id == None):
			messages.add_message(request, messages.INFO, 'object id is missing')
			return render_to_response('config/object/list.html', { 'objects': LBEObject.objects.all() })
		else:
			objectForm = LBEObjectForm(instance=lbeObject)
		attForm = LBEAttributeInstanceForm()
		return render_to_response('ajax/config/modify.html',{'lbeObject': lbeObject,'objectForm': objectForm, 'attributeForm': attForm})
	
def showAttributeAJAX(request,attribute = None):
	if request.is_ajax():
		if attribute == None or attribute == '':
			attr = []
		else:
			attr = LBEAttribute.objects.filter(name__contains=attribute)[:5] # LIKE '%attribute%'
		return render_to_response('ajax/common/list.html',{'attributes': attr,'value':attribute})

@csrf_exempt
def addObjectAttribute(request, obj_id):
	if request.method == 'POST':
		form = LBEAttributeInstanceForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('/config/object/modify/' + obj_id)
		else:
			# TODO: manage errors
			print form.errors
	return redirect('/config/object/modify/' + obj_id)
