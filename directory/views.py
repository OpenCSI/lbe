# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from directory.models import *
from directory.forms import *
from services.object import LBEObjectInstanceHelper
from django.template import RequestContext
from services.backend import BackendHelper, BackendObjectAlreadyExist
from django.contrib import messages
from django.forms.formsets import formset_factory

from django import forms

def index(request):
    backend = BackendHelper()
    objects = backend.searchObjects(LBEObjectTemplate.objects.get(name='employee'))
    lbeObject = LBEObjectTemplate.objects.get(name__iexact="employee")
    return render_to_response('directory/default/index.html', { 'objects': objects,'lbeObjectId': lbeObject.id }, context_instance=RequestContext(request))

def deleteObjectInstance(request, objectName):
    backend = BackendHelper()
    objects = backend.searchObjects(LBEObjectTemplate.objects.get(name='employee'))
    return render_to_response('directory/default/index.html', { 'objects': objects }, context_instance=RequestContext(request))

#@managel_acl()
def viewObjectInstance(request,obj_id,objectName = None):
	instanceHelper = LBEObjectInstanceHelper(LBEObjectTemplate.objects.get(id=obj_id))
	obj = instanceHelper.getValuesDecompressed(objectName)
	return render_to_response('directory/default/object/view.html', {'object':obj}, context_instance=RequestContext(request))
	
# Create an instance of LBEObjectInstance from LBEObject definition. Save it into MongoDB with status AWAITING_SYNC
def addObjectInstance(request, lbeObject_id = None):
    form = None
    if request.method == 'POST':
        form = LBEObjectInstanceForm(LBEObjectTemplate.objects.get(id = lbeObject_id), request.POST)
        helper = LBEObjectInstanceHelper(LBEObjectTemplate.objects.get(id = lbeObject_id))
        if form.is_valid():
            helper.createFromDict(request)
            try:
                helper.save()
            except BackendObjectAlreadyExist as e:
                messages.add_message(request, messages.ERROR, 'Object already exists')
                return render_to_response('directory/default/object/add.html', { 'form': form, 'lbeObjectId': lbeObject_id }, context_instance=RequestContext(request))
            # Redirect to list
            return redirect('/directory/')
        else:
            render_to_response('directory/default/object/add.html', { 'form': form, 'lbeObjectId': lbeObject_id }, context_instance=RequestContext(request))
        return render_to_response('directory/default/object/add.html', { 'form': form, 'lbeObjectId': lbeObject_id }, context_instance=RequestContext(request))
    else:
        if lbeObject_id is None:
            # TODO: Redirect to a form to choose which object to add
            print 'error'
    form = LBEObjectInstanceForm(LBEObjectTemplate.objects.get(id = lbeObject_id))
    return render_to_response('directory/default/object/add.html', { 'form': form, 'lbeObjectId': lbeObject_id }, context_instance=RequestContext(request))

#@manage_acl()    
def manageObjectInstance(request, obj_id,uid,type):
	lbeObject = LBEObjectTemplate.objects.get(id=obj_id)
	lbeAttribute = LBEAttributeInstance.objects.filter(lbeObjectTemplate=lbeObject)
	instanceHelper = LBEObjectInstanceHelper(lbeObject)
	# Get multiValue attributes: ('+' button)
	multivalue = []
	# get all attributInstance of ObjectTemplate:
	attributeInstance = LBEAttributeInstance.objects.filter(lbeObjectTemplate=lbeObject)
	for attribute in attributeInstance:
		# check if multivalue is checked (True):
		if attribute.multivalue:
			multivalue.append(attribute.lbeAttribute.name)
	if request.method == 'POST':
		# Modify part:
		form = instanceHelper.form(uid,request.POST)
		if form.is_valid():
			instanceHelper.updateFromDict(uid,form.clean())
			instanceHelper.modify()
			messages.add_message(request, messages.SUCCESS, 'Object saved')
	else:
		# Set values into form:
		form = instanceHelper.form(uid)
	# Show part:
	return render_to_response('directory/default/object/manage.html',{'form':form,'lbeObjectId':obj_id,'lbeAttribute':lbeAttribute,'uid':uid,'multivalue':multivalue},context_instance=RequestContext(request))

# REMOVE:
#@manage_acl('modify')
def modifyObjectInstance(request,obj_id,uid):
	return HttpResponse('')
	
#@manage_acl('delete')
#def deleteObjectInstance(request,obj_id,uid):
#	return HttpResponse('')
