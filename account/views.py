# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from directory.models import LBEDirectoryACL, LBEObjectTemplate
from services.ACL import ACLHelper


@login_required
def right(request):
    # Get all objects:
    objects = LBEObjectTemplate.objects.all()
    listACLsObjects = []
    # Test differents Object's ACLs for the User:
    for obj in objects:
        ACLsObjects = dict()
        #            R   ,  C  ,  U  ,  A  ,  D
        ACLsType = (False, False, False, False, False)
        ACLsType = list(ACLsType)
        ACLsObjects[obj.displayName] = ACLsType
        ACLs = LBEDirectoryACL.objects.filter(object=obj)
        for acl in ACLs:
            if acl.type == "select" and ACLsType[0] == False:
                aclHelper = ACLHelper(obj, acl.condition)
                ACLsType[0] = aclHelper.execute(str(request.user))
            elif acl.type == "create" and ACLsType[1] == False:
                aclHelper = ACLHelper(obj, acl.condition)
                ACLsType[1] = aclHelper.execute(str(request.user))
            elif acl.type == "update" and ACLsType[2] == False:
                aclHelper = ACLHelper(obj, acl.condition)
                ACLsType[2] = aclHelper.execute(str(request.user))
            elif acl.type == "approval" and ACLsType[3] == False:
                aclHelper = ACLHelper(obj, acl.condition)
                ACLsType[3] = aclHelper.execute(str(request.user))
            elif acl.type == "delete" and ACLsType[4] == False:
                aclHelper = ACLHelper(obj, acl.condition)
                ACLsType[4] = aclHelper.execute(str(request.user))
        listACLsObjects.append(ACLsObjects)
    return render_to_response('user/acl.html', {'acls': listACLsObjects}, context_instance=RequestContext(request))
