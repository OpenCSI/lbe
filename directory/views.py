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
			attr = request.GET.keys()[nb].split('_')[0]# attribute name without the number.
			attribute = LBEAttribute.objects.get(name__iexact=attr)
			attributeInstance = LBEAttributeInstance.objects.get(lbeObjectTemplate=lbeObject,lbeAttribute=attribute)
			# Form:
			js = "save(\'/directory/object/manage/"+obj_id+"/"+uid+"','"+attr+"',$(\'#id_"+attr+"').val(),'"+request.GET.keys()[nb].split('_')[1]+"');"
			f = LBEAttributeSingle(lbeAttribute=attributeInstance,defaultValue=request.GET[request.GET.keys()[nb]],event='onBlur',js=js)
			# no value: not modified
			if not f.visible_fields() == []:
				html = str(f.visible_fields()[0])
			else:
				html = request.GET[request.GET.keys()[nb]]
		elif type == 'check':
			if request.method != 'GET':# no value:
				html = -2
			else:
				if request.GET[request.GET.keys()[0]] == '':# empty value:
					html = -1
				else:# check if value is correct:
					lbeObjectInstance = LBEObjectInstance(lbeObject)
					if lbeObjectInstance.is_valid(request.GET):
						html = 0
					else:
						html = -2
					#html = 0 # 0: no error; -1: error (empty); -2: wrong checking 
		elif type == 'save':
			lbeObjectInstance = LBEObjectInstance(lbeObject)
			# check value before saving:
			if lbeObjectInstance.is_valid(request.GET):
				# save value (replace):
				helper = LBEObjectInstanceHelper(LBEObjectTemplate.objects.get(id = obj_id))
				helper.updateFromDict(uid,request.GET)
				helper.modify()
			html = request.GET[request.GET.keys()[nb]]
		elif type == 'delete':
			# test if value exists from attribute value:
			helper = LBEObjectInstanceHelper(LBEObjectTemplate.objects.get(id = obj_id))
			remove = helper.removeFromDict(uid,request.GET)
			helper.modify()
			# if not: remove the attribute value
			if remove:
				html = 'delete'
			else:
				html = 'empty'
			# else set empty string value
		elif type == 'add':
			# ModalBox:
			if request.method == 'GET' and request.GET.has_key('attribute'):
				attribute = LBEAttribute.objects.get(name__iexact=request.GET['attribute'])
				# input (widget):
				attributeInstance = LBEAttributeInstance.objects.get(lbeObjectTemplate=lbeObject,lbeAttribute=attribute)
				if attributeInstance.widget == 'forms.CharField':
					event='onKeyUp'
				else:
					event='onChange'
				js = "check(\'/directory/object/manage/"+obj_id+"/"+uid+"/check\','"+attribute.name+"',$(\'#id_"+attribute.name+"').val());"
				widget = LBEAttributeSingle(lbeAttribute=attributeInstance,defaultValue="",event=event,js=js)
				return render_to_response('ajax/directory/addAttribute.html',{'user':uid,'attribute':attribute,'widget':widget,'uid':uid,'lbeObjectId':obj_id})
			# Save part:
			else:
				try:
					# add value:
					# Before adding; need to check (again) value
					lbeObjectInstance = LBEObjectInstance(lbeObject)
					if lbeObjectInstance.is_valid(request.GET):
						helper = LBEObjectInstanceHelper(LBEObjectTemplate.objects.get(id = obj_id))
						helper.updateFromDict(uid,request.GET)
						helper.modify()
						# need to update virtual attributes too [TODO]
						html = 'Value added.'
						html += '<script type="text/javascript">location.reload();</script>'
					else:
						raise BaseException('Check values are incorrect.')
				except BaseException as e:
					print 'Error to add value: ' + str(e)
					html = '(!) Value not added'
		return HttpResponse(html)
		# END AJAX PART.
	backend = BackendHelper()
	objectValue = backend.getObjectByName(lbeObject,uniqueName=uid)
	return render_to_response('directory/default/object/manage.html',{'object':objectValue,'lbeObjectId':lbeObject.id,'lbeAttribute':lbeAttribute,'uid':uid},context_instance=RequestContext(request))

#@manage_acl('modify')
def modifyObjectInstance(request,obj_id,uid):
	return HttpResponse('')
