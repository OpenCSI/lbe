from django.contrib import admin
from directory.models import LBEAttribute, LBEObjectTemplate, LBEObjectClass

class LBEAttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'displayName')

class LBEObjectAdmin(admin.ModelAdmin):
    pass
    
class LBEObjectClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'name')

admin.site.register(LBEAttribute, LBEAttributeAdmin)
admin.site.register(LBEObjectTemplate, LBEObjectAdmin)
admin.site.register(LBEObjectClass, LBEObjectClassAdmin)
