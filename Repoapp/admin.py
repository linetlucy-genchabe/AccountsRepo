from django.contrib import admin
from .models import *
# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    filter_horizontal = ['allowed_countries', 'allowed_counties', 'allowed_subcounties']

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Category)
admin.site.register(Accounts)
admin.site.register(Subcounty)
admin.site.register(County)
admin.site.register(Dashboards)
admin.site.register(Countries)