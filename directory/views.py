# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from directory.models import *
from directory.forms import *
from services.object import LBEObjectInstanceHelper
from django.template import RequestContext
from services.backend import BackendHelper, BackendObjectAlreadyExist
from django.contrib import messages
from django.forms.formsets import formset_factory
import math

from django import forms

@login_required
def index(request,lbeObject_id=1,page=1):
    print request
	# init object:
    if lbeObject_id is None:
		lbeObject_id = 1
    lengthMax=10
    # init pagination:
    if page is None:
		page=1
    if int(page)-lengthMax < 0:
		index = 0
    else:
        index = int(page)-lengthMax
    backend = BackendHelper()
    objects = backend.searchObjects(LBEObjectTemplate.objects.get(id=lbeObject_id),index,lengthMax)
    lbeObject = LBEObjectTemplate.objects.get(id=lbeObject_id)
    lbeObjects = LBEObjectTemplate.objects.all()
    # Pagination:
    size = int(math.ceil(backend.lengthObjects(LBEObjectTemplate.objects.get(id=lbeObject_id))/ float(lengthMax)))
    tabSize = []
    for i in range(0,size):
        tabSize.append(i+1)
    return render_to_response('directory/default/index.html', { 'objects': objects,'lbeObjectId': lbeObject.id,'lbeObjects':lbeObjects, 'length': tabSize,'page': int(page) }, context_instance=RequestContext(request))

# REMOVE object
#@manage_acl('delete')
@login_required
def deleteObjectInstance(request,lbeObject_id,objectName):
    backend = BackendHelper()
    lbeObject = LBEObjectTemplate.objects.get(id=lbeObject_id)
    # change status code user:
    instanceHelper = LBEObjectInstanceHelper(lbeObject)
    instanceHelper.remove(objectName)
    # Current page from the object deleted:
    position = backend.positionObject(lbeObject.name,objectName)
    lengthMax = 10
    page = int(math.ceil(position/float(lengthMax)))
    return index(request,lbeObject_id,page)

#@manage_acl('view')
@login_required
def viewObjectInstance(request,obj_id,objectName = None):
	instanceHelper = LBEObjectInstanceHelper(LBEObjectTemplate.objects.get(id=obj_id))
	obj = instanceHelper.getValuesDecompressed(objectName)
	return render_to_response('directory/default/object/view.html', {'object':obj,'obj_id':obj_id}, context_instance=RequestContext(request))
	
# Create an instance of LBEObjectInstance from LBEObject definition. Save it into MongoDB with status AWAITING_SYNC
#@manage_acl('create')
@login_required
def addObjectInstance(request, lbeObject_id = None):
    form = None
    helper = LBEObjectInstanceHelper(LBEObjectTemplate.objects.get(id = lbeObject_id))
    if request.method == 'POST':
        form = helper.form(LBEObjectTemplate.objects.get(id = lbeObject_id), request.POST)
        if form.is_valid():
            helper.createFromDict(request)
            try:
                helper.save()
            except BackendObjectAlreadyExist as e:
                messages.add_message(request, messages.ERROR, 'Object already exists')
                return render_to_response('directory/default/object/add.html', { 'form': form, 'lbeObjectId': lbeObject_id }, context_instance=RequestContext(request))
            # Redirect to list
            return redirect('/directory/')
        return render_to_response('directory/default/object/add.html', { 'form': form, 'lbeObjectId': lbeObject_id }, context_instance=RequestContext(request))
    else:
        if lbeObject_id is None:
            # TODO: Redirect to a form to choose which object to add
            print 'error'
    form = helper.form(LBEObjectTemplate.objects.get(id = lbeObject_id))
    return render_to_response('directory/default/object/add.html', { 'form': form, 'lbeObjectId': lbeObject_id }, context_instance=RequestContext(request))

# Modify, remove values
#@manage_acl() 
@login_required   
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

@login_required
def searchAJAX(request, obj_id, search):
    if len(search) == 0:
        return HttpResponse('/')
    backend = BackendHelper()
    objects = backend.searchObjectsByPattern(LBEObjectTemplate.objects.get(id=obj_id),search)
    print objects
    return render_to_response('ajax/directory/search.html', { 'lbeObjectId':obj_id, 'objects': objects}, context_instance=RequestContext(request))

