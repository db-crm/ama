from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(department)
admin.site.register(division)
admin.site.register(area)
admin.site.register(process_assessment)
admin.site.register(technology_staff)