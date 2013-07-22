from django.contrib import admin
from directory.models import LBEAttribute, LBEObjectTemplate


class LBEAttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'displayName')


class LBEObjectAdmin(admin.ModelAdmin):
    pass


class LBEObjectClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'name')


admin.site.register(LBEAttribute, LBEAttributeAdmin)
admin.site.register(LBEObjectTemplate, LBEObjectAdmin)
