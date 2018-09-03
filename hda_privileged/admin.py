from django.contrib import admin
from .import models

# Register your models here.
admin.site.register(models.US_States)
admin.site.register(models.US_Counties)
admin.site.register(models.Data_Point)
admin.site.register(models.Data_Set)
admin.site.register(models.Indicators)