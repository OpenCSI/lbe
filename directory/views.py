# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect
from directory.models import *
from directory.forms import *
from services.object import LBEObjectInstanceHelper
from django.template import RequestContext
from services.backend import BackendHelper, BackendObjectAlreadyExist
from django.contrib import messages

def index(request):
    backend = BackendHelper()
    objects = backend.searchObjects(LBEObjectTemplate.objects.get(name='employee'))
    return render_to_response('directory/default/index.html', { 'objects': objects }, context_instance=RequestContext(request))

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