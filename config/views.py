# -*- coding: utf-8 -*-
from django.contrib.admin.views.decorators import staff_member_required 
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.template import RequestContext
from directory.models import *
from directory.forms import *
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse

from services.ACL import ACLHelper
from services.backend import BackendHelper
from services.target import TargetHelper

@staff_member_required
def addObject(request):
    if request.method == 'POST':
        form = LBEObjectTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/config/object/list')
    else:
        form = LBEObjectTemplateForm()
    # which attribute have ajax request:
    ajaxAttribute = 'instanceNameAttribute'
    # Ajax function to call (js):
    ajaxFunction = 'selectFrom(\'' + reverse('config.views.showAttributeAJAX')[:-1] +'\',\''+ajaxAttribute+'\');'
    return render_to_response('config/object/create.html', { 'objectForm': form,'ajaxAttribute':ajaxAttribute,'ajaxFunction':ajaxFunction }, context_instance=RequestContext(request))

@staff_member_required
def listObjects(request):
    return render_to_response('config/object/list.html', { 'objects': LBEObjectTemplate.objects.all() }, context_instance=RequestContext(request))

@staff_member_required
def modifyObject(request, obj_id = None, instance_id = None):
    objectForm = None
    lbeObjectTemplate = LBEObjectTemplate.objects.get(id = obj_id)
    if request.method == 'POST':
        objectForm = LBEObjectTemplateForm(request.POST, instance = lbeObjectTemplate)
        oldNAttribute = lbeObjectTemplate.instanceNameAttribute.name
        oldDNAttribute = lbeObjectTemplate.instanceDisplayNameAttribute.id
        if objectForm.is_valid():
			# change the _id value if changed:
            if not oldNAttribute == request.POST['instanceNameAttribute']:
				changeID = True
            else:
				changeID = False
            # change the displayName value if changed:
            if not oldDNAttribute == int(request.POST['instanceDisplayNameAttribute']):
				DN = True
            else:
				DN = False
            if changeID or DN:
				if not lbeObjectTemplate.needReconciliationRDN:
					objectForm.instance.instanceNameBeforeAttribute = LBEAttribute.objects.get(name__iexact=oldNAttribute)
					objectForm.instance.needReconciliationRDN = True
				backend = BackendHelper()
				ob = backend.searchObjects(lbeObjectTemplate)
				try:
					for o in ob:
						if changeID:
							backend.update_id(lbeObjectTemplate,o,o.attributes[request.POST['instanceNameAttribute']][0])
							# the RDN Attribute from Target Server is replace into the Reconciliation
						if DN:
							attribute = LBEAttribute.objects.get(id = request.POST['instanceDisplayNameAttribute'])
							backend.modifyDisplayName(lbeObjectTemplate,o.name,o.attributes[attribute.name][0])
				except KeyError:
					messages.add_message(request, messages.ERROR, 'Error while saving object, "' + request.POST['instanceNameAttribute'] + '" does not exist for the Object.')
					return redirect('/config/object/modify/' + obj_id)
            objectForm.save()
            messages.add_message(request, messages.SUCCESS, 'Object saved')
            return redirect('/config/object/modify/' + obj_id)
        else:
            messages.add_message(request, messages.ERROR, 'Error while saving object.')
    else:
        if (obj_id == None):
            messages.add_message(request, messages.INFO, 'Object id is missing.')
            return render_to_response('config/object/list.html', { 'objects': LBEObjectTemplate.objects.all() })
        else:
            objectForm = LBEObjectTemplateForm(instance= lbeObjectTemplate)
    attForm = LBEAttributeInstanceForm()
    instances = LBEAttributeInstance.objects.filter(lbeObjectTemplate = lbeObjectTemplate)
    # which attribute have ajax request:
    ajaxAttribute = 'instanceNameAttribute'
    defaultValue = lbeObjectTemplate.instanceNameAttribute.name
    # Ajax function to call (js):
    ajaxFunction = 'selectFrom(\'' + reverse('config.views.showAttributeAJAX')[:-1] +'\',\''+ajaxAttribute+'\');'
    return render_to_response('config/object/modify.html', { 'attributeInstances': instances, 'lbeObject': lbeObjectTemplate, 'objectForm': objectForm, 'attributeForm': attForm,'ajaxAttribute':ajaxAttribute,'ajaxFunction':ajaxFunction,'defaultValue':defaultValue},\
        context_instance=RequestContext(request))

"""
Function enables to show a attributes list 
for the 'Instancenameattribute' of Object:
"""
@staff_member_required
def showAttributeAJAX(request,attribute = None,value = None):
	if request.is_ajax():
		if value == None or value == '':
			attr = []
		else:
			attr = LBEAttribute.objects.filter(name__contains=value)[:5] # LIKE '%attribute%'
		return render_to_response('ajax/config/listAttributes.html',{'attributes': attr,'value':attribute,'attr':attribute}, context_instance=RequestContext(request))

@staff_member_required
def addAttributeToObject(request,obj_id = None):
    lbeObjectTemplate = LBEObjectTemplate.objects.get(id = obj_id)
    if request.method == 'POST':
        form = LBEAttributeInstanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Attribute added.')
            reloadParent = '<script>window.opener.location.reload();window.close();</script>'
        else:
            reloadParent = ''
            messages.add_message(request, messages.ERROR, 'Error while adding attribute.')
    else:
	    if (obj_id == None):
		    messages.add_message(request, messages.INFO, 'Object id is missing.')
	    form = LBEAttributeInstanceForm()
	    reloadParent = ''
    return render_to_response('config/object/attributes/addAttribute.html',{'objID': obj_id, 'attributeForm': form,'reloadParent':reloadParent}, context_instance=RequestContext(request))

@staff_member_required
def modifyAttributeToObject(request,obj_id,attr_id = None):
	attribute = LBEAttributeInstance.objects.get(id = attr_id)
	if request.method == 'POST':
		form = LBEAttributeInstanceForm(request.POST,instance=attribute)
		if form.is_valid():
			form.save()
			messages.add_message(request, messages.SUCCESS, 'Attribute managed.')
			reloadParent = '<script>window.opener.location.reload();window.close();</script>'
		else:
			reloadParent = ''
			messages.add_message(request, messages.ERROR, 'Error while adding attribute.')
	else:
		if (attr_id == None):
			messages.add_message(request, messages.INFO, 'Attribute id is missing.')
		else:
			reloadParent = ''
			form = LBEAttributeInstanceForm(instance=attribute)
	return render_to_response('config/object/attributes/manageAttribute.html',{'attributeForm': form,'attrID':attr_id,'objID':obj_id,'reloadParent':reloadParent}, context_instance=RequestContext(request))
	
@staff_member_required
def addAttribute(request):
	if request.method == 'POST':
		form = LBEAttributeForm(request.POST)
		if form.is_valid():
			form.save()
			messages.add_message(request, messages.SUCCESS, 'Attribute created.')
			return redirect('/config/attribute/add')
		else:
			messages.add_message(request, messages.ERROR, 'Error while creating attribute.')
	else:
		form = LBEAttributeForm()
	return render_to_response('config/attribute/create.html',{'attributeForm':form},context_instance=RequestContext(request))

@staff_member_required
def modifyAttribute(request,attribute_id = 1):
	if attribute_id is None:
		attribute_id = 1
	attributes = LBEAttribute.objects.all()
	form = []
	if request.method == "POST":
		form = LBEAttributeModifyForm(request.POST,instance = LBEAttribute.objects.get(id=attribute_id))
		if form.is_valid():
			form.save()
			messages.add_message(request, messages.SUCCESS, 'Attribute Modified.')
		else:
			messages.add_message(request, messages.ERROR, 'Attribute not modified.')
	else:	
		try:
			form = LBEAttributeModifyForm(instance = LBEAttribute.objects.get(id=attribute_id))
		except BaseException:
			try:
				form = LBEAttributeModifyForm(instance = attributes[0])
			except BaseException:
				pass
	return render_to_response('config/attribute/modify.html',{'attributes':attributes,'attributeForm':form,'attribute_id':attribute_id},context_instance=RequestContext(request))
	
@staff_member_required
def removeAttribute(request,attribute_id = None):
	try:
		attribute = LBEAttribute.objects.get(id=attribute_id)
		if LBEAttributeInstance.objects.filter(lbeAttribute=attribute):
			messages.add_message(request, messages.ERROR, 'Cannot remove attributes used. Check the different instance object.')
		else:
			attribute.delete()
			messages.add_message(request, messages.SUCCESS, 'Attribute removed.')
	except BaseException as e:
		print e
		messages.add_message(request, messages.ERROR, 'Error while removing attribute.')
	return HttpResponseRedirect('/config/attribute/modify')
		
@staff_member_required
def modifyInstanceAttribute(request,obj_id = None,attr_id = None):
	if request.method == 'POST':
		if obj_id == None:
			messages.add_message(request, messages.SUCCESS, 'Cannot modify attribute without object.')
			redirect('/config/object/add/')
		form = LBEAttributeInstanceForm(request.POST,instance = LBEAttributeInstance.objects.get(id=attr_id))
		if form.is_valid():
			form.save()
			messages.add_message(request, messages.SUCCESS, 'Attribute modified.')
		else:
			messages.add_message(request, messages.ERROR, 'Attribute not modified.')
			print form.errors
	return redirect('/config/object/modify/' + obj_id)

@staff_member_required
def removeInstanceAttribute(request,obj_id = None,attr_id = None):
	try:
		LBEAttributeInstance.objects.get(id=attr_id).delete()
		messages.add_message(request,messages.SUCCESS,'Intance Attribute removed.')
	except BaseException as e:
		messages.add_message(request,messages.ERROR,'Error to remove the Instance Attribute.')
	return redirect('/config/object/modify/' + obj_id)

@staff_member_required
def addReference(request):
	if request.method == 'POST':
		form = LBEReferenceForm(request.POST)
		if form.is_valid():
			form.save()
			messages.add_message(request, messages.SUCCESS, 'Reference created.')
			return redirect('/config/reference/add')
		else:
			messages.add_message(request, messages.ERROR, 'Error while creating reference.')
	else:
		form = LBEReferenceForm()
	return render_to_response('config/reference/add.html',{'referenceForm':form},context_instance=RequestContext(request))

@staff_member_required
def modifyReference(request,ref_id = 1):
	referencesList = LBEReference.objects.all()
	try:
		ref = LBEReference.objects.get(id = ref_id)
	except BaseException:
		try:
			ref = referencesList[0]
		except:
			ref = []
	if request.method == 'POST':
		try:
			form = LBEReferenceForm(request.POST,instance=ref)
			if form.is_valid():
				form.save()
				messages.add_message(request, messages.SUCCESS, 'Reference modified.')
				return redirect('/config/reference/modify')
			else:
				messages.add_message(request, messages.ERROR, 'Error while modifing reference: check if you have respected the form.')
		except BaseException as e:
			messages.add_message(request, messages.ERROR, 'Error while modifing reference.')
	else:
		try:
			form = LBEReferenceForm(instance=ref)
		except BaseException:
			form = []
	return render_to_response('config/reference/modify.html',{'referenceForm':form,'references':referencesList,'refID':ref_id},context_instance=RequestContext(request))

@staff_member_required	
def removeReference(request,ref_id = None):
	try:
		reference = LBEReference.objects.get(id=ref_id)
		# Remove all instance attributes which use the reference:
		LBEAttributeInstance.objects.filter(reference = reference).delete()
		reference.delete()
		messages.add_message(request,messages.SUCCESS,'Reference removed.')
	except BaseException:
		messages.add_message(request,messages.ERROR,'Error to remove the reference.')
	return redirect('/config/reference/modify/')


@staff_member_required	
def addScript(request):
	if request.method == 'POST':
		form = LBEScriptForm(request.POST,request.FILES)
		if form.is_valid():
			scriptDB = form.save()
			if scriptDB:
				messages.add_message(request, messages.SUCCESS, 'script added.')
			else:
				messages.add_message(request,messages.ERROR, 'script not added.')
				scriptDB.delete()
			return redirect('/config/script/add')
		else:
			messages.add_message(request, messages.ERROR, 'Error while adding script file.')
	else:
		form = LBEScriptForm()
	return render_to_response('config/script/add.html',{'scriptForm':form},context_instance=RequestContext(request))
	
@staff_member_required
def manageScript(request,scriptId = None):
	if scriptId == None:
		scriptId = 1
	scriptList = LBEScript.objects.all()
	script = LBEScript.objects.get(id = scriptId)
	if request.method == 'POST':
		form = LBEScriptForm(request.POST,instance=script)
		if form.is_valid():
			if form.save():
				messages.add_message(request, messages.SUCCESS, 'script managed.')
		else:
			messages.add_message(request, messages.ERROR, 'Error while managing the script file.')
	else:
		form = LBEScriptForm(instance=script)
	return render_to_response('config/script/manage.html',{'scriptForm':form, 'scriptList':scriptList,'scriptId':scriptId},context_instance=RequestContext(request))

@staff_member_required
def addACL(request):
	if request.method == 'POST':
		form = LBEACLForm(request.POST)
		if form.is_valid():
			form.save()
			messages.add_message(request, messages.SUCCESS, 'ACL created.')
			return redirect('/config/acl/add')
		else:
			messages.add_message(request, messages.ERROR, 'Error while adding ACL.')
	else:
		form = LBEACLForm()
	return render_to_response('config/acl/create.html',{'aclForm':form},context_instance=RequestContext(request))
	
@staff_member_required
def manageACL(request, aclId = None):
	aclList = LBEDirectoryACL.objects.all()
	try:
		if aclId == None:
			form = LBEACLForm(instance=aclList[0])
			aclId = aclList[0].id
		if request.method == 'POST':
				form = LBEACLForm(request.POST,instance=LBEDirectoryACL.objects.get(id=aclId))
				if form.is_valid():
					if form.save():
						messages.add_message(request, messages.SUCCESS, 'ACL managed.')
				else:
					messages.add_message(request, messages.ERROR, 'Error while adding ACL.')
		else:
			form = LBEACLForm(instance=LBEDirectoryACL.objects.get(id=aclId))
	except BaseException:
		form = None
	return render_to_response('config/acl/manage.html',{'aclList':aclList,'aclForm':form,'aclId':aclId},context_instance=RequestContext(request))

@staff_member_required
def removeACL(request,aclId = None):
	try:
		LBEDirectoryACL.objects.get(id=aclId).delete()
		messages.add_message(request,messages.SUCCESS,'ACL removed.')
	except BaseException:
		messages.add_message(request,messages.ERROR,'Error to remove the ACL.')
	return redirect('/config/acl/manage/')

@staff_member_required
def checkACL_AJAX(request,query = None):
	if request.is_ajax():
		acl = ACLHelper(None,query)
		acl.check()
		return HttpResponse(acl.traceback)
	return HttpResponse('')
