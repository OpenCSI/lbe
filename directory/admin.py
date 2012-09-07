from django.contrib import admin
from directory.models import LBEAttribute, LBEObject, LBEObjectClass

class LBEAttributeAdmin(admin.ModelAdmin):
	list_display = ('name', 'displayName')

class LBEObjectAdmin(admin.ModelAdmin):
	pass

class LBEObjectClassAdmin(admin.ModelAdmin):
	pass

admin.site.register(LBEAttribute, LBEAttributeAdmin)
admin.site.register(LBEObject, LBEObjectAdmin)
admin.site.register(LBEObjectClass, LBEObjectClassAdmin)