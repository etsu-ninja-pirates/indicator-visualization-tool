from django.contrib import admin
from .models import US_States, US_Counties, Data_Point, Data_Set, Indicators

# Register your models here.
@admin.register(US_States)
class USStates(admin.ModelAdmin):
    fields = ['abbreviation', 'state_name', 's_fips']

@admin.register(US_Counties)
class USCounties(admin.ModelAdmin):
    fields = ['s_fips', 'abbrev', 'county_name', 'c_fips']

@admin.register(Data_Point)
class DataPoint(admin.ModelAdmin):
    fields = []
@admin.register(Data_Set)
class DataSet(admin.ModelAdmin):
    fields = []
@admin.register(Indicators)
class HIndicators(admin.ModelAdmin):
    fields = []