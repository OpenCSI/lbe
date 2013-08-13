# -*- coding: utf-8 -*-
from django import template
register = template.Library()

from directory.models import LBEGroup, LBEObjectTemplate

@register.inclusion_tag("menu.html")
def showMenu():
    objects = LBEObjectTemplate.objects.all()
    groups = LBEGroup.objects.all()
    return {'objects': objects, 'groups': groups}