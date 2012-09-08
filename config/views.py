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
	return render_to_response('config/object/create.html', { 'objectForm': form })

def listObjects(request):
	return render_to_response('config/object/list.html', { 'objects': LBEObject.objects.all() })

def modifyObject(request, obj_id = None):
	if request.method == 'POST':
		print 'do nothing atm'
		# add current object in the path
		return HttpResponseRedirect('/admin/object/modify')
	else:
		if (obj_id == None):
			return render_to_response('manage/object/list.html', { 'objects': LBEObject.objects.all() })
		lbeObject = LBEObject.objects.get(id = obj_id)
		objectForm = LBEObjectForm(instance = lbeObject)
		attForm = LBEAttributeInstanceForm()
		instances = LBEAttributeInstance.objects.filter(lbeObject = lbeObject)
	return render_to_response('manage/object/modify.html', { 'attributeInstances': instances, 'lbeObject': lbeObject,'objectForm': objectForm, 'attributeForm': attForm, \
	'admin':request.user.is_superuser,'ldapState':cLBELDAP.state(),'mongoState':cLBENoSQL.state(),'username':request.user } )
