from django.contrib import admin

from .models import Sender, UtestidMapping


class SenderAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
admin.site.register(Sender, SenderAdmin)


class UtestidMappingAdmin(admin.ModelAdmin):
    list_display = ('sender', 'utestid', 'utestid_name')
    search_fields = ('sender_name', 'utestid_name', 'utestid__name')
admin.site.register(UtestidMapping, UtestidMappingAdmin)
