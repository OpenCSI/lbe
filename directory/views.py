# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from directory.models import *
from directory.forms import *
from services.object import LBEObjectInstanceHelper
from django.template import RequestContext
from services.backend import BackendHelper, BackendObjectAlreadyExist
from django.contrib import messages

from django import forms

def index(request):
    backend = BackendHelper()
    objects = backend.searchObjects(LBEObjectTemplate.objects.get(name='employee'))
    lbeObject = LBEObjectTemplate.objects.get(name__iexact="employee")
    return render_to_response('directory/default/index.html', { 'objects': objects,'lbeObjectId': lbeObject.id }, context_instance=RequestContext(request))

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
	# BEGIN AJAX PART:
	if request.is_ajax():
		nb = 0
		if type == 'modify':
			# get dynamic single input type from forms:
			attribute = LBEAttribute.objects.get(name__iexact=request.GET.keys()[nb])
			attributeInstance = LBEAttributeInstance.objects.get(lbeObjectTemplate=lbeObject,lbeAttribute=attribute)
			# Form:
			js = "save(\'/directory/object/manage/"+obj_id+"/"+uid+"','"+request.GET.keys()[nb]+"',$(\'#id_"+request.GET.keys()[nb]+"').val());"
			f = LBEAttributeSingle(lbeAttribute=attributeInstance,defaultValue=request.GET[request.GET.keys()[nb]],event='onBlur',js=js)
			# no value: not modified
			if not f.visible_fields() == []:
				html = str(f.visible_fields()[0])#[:-2] + ' onBlur="save(\'/directory/object/manage/'+obj_id+'/'+uid+'\',\''+request.GET.keys()[nb]+'\',$(\'#id_'+request.GET.keys()[nb]+'\').val());">'
			else:
				html = request.GET[request.GET.keys()[nb]]
			#html = '<input type="text" name="'+ request.GET.keys()[nb] +'" id="'+request.GET.keys()[nb]+'" value="'+request.GET[request.GET.keys()[nb]]+'" onBlur="save(\'/directory/object/manage/'+obj_id+'/'+uid+'\',\''+request.GET.keys()[nb]+'\',$(\'#'+request.GET.keys()[nb]+'\').val());"/>'
		elif type == 'save':
			# TODO: check here value's format
			html = request.GET[request.GET.keys()[nb]]
			# save value (replace):
			helper = LBEObjectInstanceHelper(LBEObjectTemplate.objects.get(id = obj_id))
			helper.updateFromDict(uid,request.GET)
			helper.modify()
		# elif type == 'add':
			# TODO
		return HttpResponse(html)
		# END AJAX PART.
	backend = BackendHelper()
	objectValue = backend.getObjectByName(lbeObject,uniqueName=uid)
	return render_to_response('directory/default/object/manage.html',{'object':objectValue,'lbeObjectId':lbeObject.id,'lbeAttribute':lbeAttribute,'uid':uid},context_instance=RequestContext(request))

#@manage_acl('modify')
def modifyObjectInstance(request,obj_id,uid):
	return HttpResponse('coucou')
