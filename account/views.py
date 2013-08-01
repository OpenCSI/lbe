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
    # Test different Object's ACLs for the User:
    for obj in objects:
        ACLsObjects = dict()
        #            R   ,  C  ,  U  ,  A  ,  D
        if not request.user.is_superuser:
            ACLsType = (False, False, False, False, False)
        else:
            ACLsType = (True, True, True, True, True)
        ACLsType = list(ACLsType)
        ACLsObjects[obj.displayName] = ACLsType
        if not request.user.is_superuser:
            ACLs = LBEDirectoryACL.objects.filter(object=obj)
            for acl in ACLs:
                if acl.type == "select" and not ACLsType[0]:
                    aclHelper = ACLHelper(obj, acl.condition)
                    ACLsType[0] = aclHelper.execute(str(request.user))
                elif acl.type == "create" and not ACLsType[1]:
                    aclHelper = ACLHelper(obj, acl.condition)
                    ACLsType[1] = aclHelper.execute(str(request.user))
                elif acl.type == "update" and not ACLsType[2]:
                    aclHelper = ACLHelper(obj, acl.condition)
                    ACLsType[2] = aclHelper.execute(str(request.user))
                elif acl.type == "approval" and not ACLsType[3]:
                    aclHelper = ACLHelper(obj, acl.condition)
                    ACLsType[3] = aclHelper.execute(str(request.user))
                elif acl.type == "delete" and not ACLsType[4]:
                    aclHelper = ACLHelper(obj, acl.condition)
                    ACLsType[4] = aclHelper.execute(str(request.user))
        listACLsObjects.append(ACLsObjects)
    return render_to_response('user/acl.html', {'acls': listACLsObjects}, context_instance=RequestContext(request))
