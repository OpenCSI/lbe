# -*- coding: utf-8 -*-
import math
import json

from django.contrib.auth.decorators import login_required
from django.utils.datastructures import SortedDict
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib import messages
from django.conf import settings

from directory.models import *
from directory.forms import *
from services.object import LBEObjectInstanceHelper
from services.group import GroupInstanceHelper
from services.backend import BackendHelper, BackendObjectAlreadyExist


@login_required
@ACLHelper.select
def index(request, lbeObject_id=1, page=1):
    # init object:
    if lbeObject_id is None:
        lbeObject_id = 1
    if settings.PAGINATION is None:
        lengthMax = 25
    else:
        lengthMax = settings.PAGINATION
        # init pagination:
    if page is None:
        page = 1
    else:
        page = int(page)
    if page == 1:
        index = 0
    else:
        index = int(page) + lengthMax - 2
    backend = BackendHelper()
    objects = backend.searchObjects(LBEObjectTemplate.objects.get(id=lbeObject_id), index, lengthMax)
    lbeObject = LBEObjectTemplate.objects.get(id=lbeObject_id)
    lbeObjects = LBEObjectTemplate.objects.all()
    # Pagination:
    size = int(math.ceil(backend.lengthObjects(LBEObjectTemplate.objects.get(id=lbeObject_id)) / float(lengthMax)))
    if page < 3:
        min = 1
    else:
        min = page - 2
    if size - page > 2:
        max = page + 2
    else:
        max = size
    tabSize = []
    tabSize.append(min)
    for i in range(min, max):
        tabSize.append(i + 1)
    return render_to_response('directory/default/index.html',
                              {'objects': objects, 'lbeObjectId': lbeObject.id, 'lbeObjects': lbeObjects,
                               'length': tabSize, 'page': int(page), 'minCPage': min, 'maxCPage': max, 'maxPage': size},
                              context_instance=RequestContext(request))


@login_required
@ACLHelper.delete
def deleteObjectInstance(request, lbeObject_id, objectName):
    backend = BackendHelper()
    lbeObject = LBEObjectTemplate.objects.get(id=lbeObject_id)
    # change status code user:
    instanceHelper = LBEObjectInstanceHelper(lbeObject)
    instanceHelper.remove(objectName)
    # Current page from the object deleted:
    position = backend.positionObject(lbeObject.name, objectName)
    lengthMax = 10
    page = int(math.ceil(position / float(lengthMax)))
    return HttpResponseRedirect('/')


@login_required
@ACLHelper.select
def viewObjectInstance(request, lbeObject_id, objectName=None):
    try:
        objectTemplate = LBEObjectTemplate.objects.get(id=lbeObject_id)
        instanceHelper = LBEObjectInstanceHelper(objectTemplate)
        obj = instanceHelper.getValuesDecompressed(objectName)
        # Replace attributes name by displayName:
        objectInstance = SortedDict()
        attributesInstance = LBEAttributeInstance.objects.filter(lbeObjectTemplate=objectTemplate).order_by("position")
        for attribute in attributesInstance:
            objectInstance[attribute.lbeAttribute.displayName] = obj[attribute.lbeAttribute.name]
        objectInstance['name'] = objectName
        objectInstance['displayName'] = obj[objectTemplate.instanceDisplayNameAttribute.name][0]
    except BaseException as e:
        objectInstance = []
    return render_to_response('directory/default/object/view.html', {'object': objectInstance, 'obj_id': lbeObject_id},
                              context_instance=RequestContext(request))


@login_required
@ACLHelper.create
def addObjectInstance(request, lbeObject_id=None):
    lbeObject = LBEObjectTemplate.objects.get(id=lbeObject_id)
    form = None
    helper = LBEObjectInstanceHelper(LBEObjectTemplate.objects.get(id=lbeObject_id))
    # Get multiValue attributes: ('+' button)
    multivalue = []
    # get all attributInstance of ObjectTemplate:
    attributeInstance = LBEAttributeInstance.objects.filter(lbeObjectTemplate=lbeObject).order_by('position')
    for attribute in attributeInstance:
        # check if multivalue is checked (True):
        if attribute.multivalue:
            multivalue.append(attribute.lbeAttribute.name)
    if request.method == 'POST':
        form = helper.form(lbeObject, request.POST)
        if form.is_valid():
            try:
                helper.createFromDict(request)
            except BaseException:
                messages.add_message(request, messages.ERROR, 'Error when creating object.')
                return render_to_response('directory/default/object/add.html',
                                          {'form': form, 'lbeObjectId': lbeObject_id, 'multivalue': multivalue},
                                          context_instance=RequestContext(request))
            try:
                helper.save()
            except BackendObjectAlreadyExist as e:
                messages.add_message(request, messages.ERROR, 'Object already exists')
                return render_to_response('directory/default/object/add.html',
                                          {'form': form, 'lbeObjectId': lbeObject_id, 'multivalue': multivalue},
                                          context_instance=RequestContext(request))
            except ValueError as e:
                messages.add_message(request, messages.ERROR, e)
                return render_to_response('directory/default/object/add.html',
                                          {'form': form, 'lbeObjectId': lbeObject_id, 'multivalue': multivalue},
                                          context_instance=RequestContext(request))
                # Redirect to list
            return redirect('/')
        return render_to_response('directory/default/object/add.html',
                                  {'form': form, 'lbeObjectId': lbeObject_id, 'multivalue': multivalue},
                                  context_instance=RequestContext(request))
    else:
        if lbeObject_id is None:
            # TODO: Redirect to a form to choose which object to add
            print 'error'
    form = helper.form(lbeObject)
    return render_to_response('directory/default/object/add.html',
                              {'form': form, 'lbeObjectId': lbeObject_id, 'multivalue': multivalue},
                              context_instance=RequestContext(request))


@login_required
@ACLHelper.update
def manageObjectInstance(request, lbeObject_id, objectName, type):
    lbeObject = LBEObjectTemplate.objects.get(id=lbeObject_id)
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
        form = instanceHelper.form(objectName, request.POST)
        if form.is_valid():
            try:
                instanceHelper.updateFromDict(objectName, form.clean())
                instanceHelper.modify()
                messages.add_message(request, messages.SUCCESS, 'Object saved')
            except ValueError as e:
                messages.add_message(request, messages.ERROR, e)
            except Exception as e:
                messages.add_message(request, messages.INFO, e)
    else:
        # Set values into form:
        form = instanceHelper.form(objectName)
    # Show part:
    return render_to_response('directory/default/object/manage.html',
                              {'form': form, 'lbeObjectId': lbeObject_id, 'lbeAttribute': lbeAttribute,
                               'uid': objectName, 'multivalue': multivalue}, context_instance=RequestContext(request))


@login_required
@ACLHelper.approval
def approvalObjectInstance(request, lbeObject_id, objectName):
    backend = BackendHelper()
    lbeObject = LBEObjectTemplate.objects.get(id=lbeObject_id)
    # change status code user:
    instanceHelper = LBEObjectInstanceHelper(lbeObject)
    instanceHelper.approval(objectName)
    # Current page from the object status changed:
    position = backend.positionObject(lbeObject.name, objectName)
    lengthMax = 10
    page = int(math.ceil(position / float(lengthMax)))
    return HttpResponseRedirect('/')#return index(request,lbeObject_id,page)


@login_required
@ACLHelper.select
def searchAJAX(request, lbeObject_id, search):
    if len(search) == 0:
        return HttpResponse('/')
    backend = BackendHelper()
    objects = backend.searchObjectsByPattern(LBEObjectTemplate.objects.get(id=lbeObject_id), search)
    return render_to_response('ajax/directory/search.html', {'lbeObjectId': lbeObject_id, 'objects': objects},
                              context_instance=RequestContext(request))


@login_required
def viewAllGroup(request):
    groups = LBEGroup.objects.all()
    groupsInstance = []
    for group in groups:
        groupInstance = GroupInstanceHelper(group)
        try:
            groupsInstance.append(groupInstance.get())
        except BaseException as e:
            print e
            pass
    return render_to_response('directory/default/group/index.html', {'groups': groupsInstance},
                              context_instance=RequestContext(request))


@login_required
def viewGroup(request, group_id):
    groupList = []
    groupName = ''
    object_id = 0
    try:
        lbeGroup = LBEGroup.objects.get(id=group_id)
        groupInstance = GroupInstanceHelper(lbeGroup)
        groupValues = groupInstance.get()
        groupName = groupValues.name
        object_id = lbeGroup.objectTemplate.id
        if not groupInstance.attributeName in groupValues.changes['set'] or groupValues.changes['set'][groupInstance.attributeName] == []:
            groupList = groupValues.attributes[groupInstance.attributeName]
        else:
            groupList = groupValues.changes['set'][groupInstance.attributeName]
    except BaseException as e:
        print e
        groupValues = []
    return render_to_response('directory/default/group/view.html', {'groupName': groupName, 'groupList': groupList,
                               'group_id': group_id, 'object_id': object_id},
                               context_instance=RequestContext(request))


@login_required
def manageGroup(request, group_id):
    try:
        lbeGroup = LBEGroup.objects.get(id=group_id)
        groupInstance = GroupInstanceHelper(lbeGroup)
        if request.method == "POST":
            form = groupInstance.form(request.POST)
            if form.is_valid():
                groupInstance.save()
                messages.add_message(request, messages.SUCCESS, "The Group is successfully saved.")
            else:
                messages.add_message(request, messages.ERROR, "Error to save the group '" + lbeGroup.name + "'")
        else:
            form = groupInstance.form()
    except BaseException as e:
        print e
    return render_to_response('directory/default/group/manage.html', {'form': form, 'group_id': group_id,
                              'attributeName': lbeGroup.objectTemplate.instanceNameAttribute.displayName,
                              'attributeMember': groupInstance.attributeName},
                              context_instance=RequestContext(request))


@login_required
def deleteGroup(request, group_id):
    try:
        group = LBEGroup.objects.get(id=group_id)
        instanceHelper = GroupInstanceHelper(group)
        instanceHelper.remove()
        messages.add_message(request,messages.SUCCESS, "group '" + group.name + "' removed.")
    except BaseException as e:
        print e
        pass
    return HttpResponseRedirect('/directory/group')


@login_required
def viewUserObjectAJAX(request, group_id, name):
    if request.is_ajax():
        group = LBEGroup.objects.get(id=group_id)
        backend = BackendHelper()
        objects = backend.searchObjectsByPattern(group.objectTemplate, name)
        list = []
        for o in objects:
            list.append(o.name)
        return HttpResponse(json.dumps(list), mimetype="application/json")


def page404(request):
    return render_to_response('error/request.html',
                              {'title': '404 Not Found', 'content': 'The page you are looking for does not exist...'},
                              context_instance=RequestContext(request))


def page500(request):
    return render_to_response('error/request.html', {'title': '505 Error Page',
                                                     'content': 'They is an error with the page, please check it later.'},
                              context_instance=RequestContext(request))
