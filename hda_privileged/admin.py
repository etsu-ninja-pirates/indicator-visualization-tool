from django.contrib import admin
from .models import *

# Register your models here.

class Data_Point_Inline(admin.TabularInline):
    model = Data_Point

class Data_Set_Inline(admin.StackedInline):
    model = Data_Set

class US_County_Inline(admin.TabularInline):
    model = US_County

@admin.register(US_State)
class US_State_Admin(admin.ModelAdmin):
    inlines = (US_County_Inline,)

    def __str__(self):
        return "US State"

@admin.register(US_County)
class US_Counties_Admin(admin.ModelAdmin):
    inlines = (Data_Point_Inline,)

@admin.register(Health_Indicator)
class Health_Indicator_Admin(admin.ModelAdmin):
    inlines = (Data_Set_Inline,)

@admin.register(Document)
class Document_Admin(admin.ModelAdmin):
    date_hierarchy = 'uploaded_at'
    readonly_fields = ('uploaded_at',)

@admin.register(Data_Set)
class Data_Set_Admin(admin.ModelAdmin):
    search_fields = ('indicator__name',)
    inlines = (Data_Point_Inline,)

@admin.register(Data_Point)
class Data_Point_Admin(admin.ModelAdmin):
    search_fields = ('county__name', 'county__state__name',)
