from django.contrib import admin
from .models import *

# Register your models here.
class UserFormAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'username', 'email', 'name', 'address', 'pin_code', 'city', 'country', 'image', 'last_login', 'is_superuser', 'is_staff', 'is_active', 'date_joined')

# class IncidentAdmin(admin.ModelAdmin):
#     list_display = ('incident_id', 'incident_details', 'identity', 'priority', 'status', 'reported_date_time', 'reporter')

admin.site.register(User, UserFormAdmin)
# admin.site.register(Incident, IncidentAdmin)