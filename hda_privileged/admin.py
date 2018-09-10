from django.contrib import admin
from .models import US_State, US_County #, Data_Point, Data_Set, Indicators

# Register your models here.
@admin.register(US_State)
class USState(admin.ModelAdmin):
    fields = ['short', 'full', 'fips']

@admin.register(US_County)
class USCounties(admin.ModelAdmin):
    fields = ['fips', 'name', 'state']

# @admin.register(Data_Point)
# class DataPoint(admin.ModelAdmin):
#     fields = []
# @admin.register(Data_Set)
# class DataSet(admin.ModelAdmin):
#     fields = []
# @admin.register(Indicators)
# class HIndicators(admin.ModelAdmin):
#     fields = []