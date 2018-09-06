import datetime
from django.db import models

# Create your models here.
class Indicators(models. Model):
    indicator_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    
class Data_Set(models.Model):
    data_id = models.BigIntegerField(primary_key=True)
    year = models.DateField()
    author = models.CharField(max_length=200)
    
    indicator_id = models.ForeignKey(Indicators, on_delete=models.CASCADE)

class US_States(models.Model): 
    # state_id = models.BigIntegerField(primary_key=True)
    abbreviation = models.CharField(primary_key=True, max_length=200)
    state_name = models.CharField(primary_key= False, max_length=200)
    s_fips = models.BigIntegerField()
    
    def __str__(self):
        return "%s  -  %s - %s" %(self.s_fips, self.abbreviation, self.state_name)

class US_Counties(models.Model):
    s_fips = models.CharField(max_length=5, default="")
    abbrev = models.ForeignKey(US_States, on_delete=models.CASCADE)
    county_name = models.CharField(max_length=200)
    c_fips = models.IntegerField(primary_key=True)

class Data_Point(models.Model):
    point_id = models.BigIntegerField(primary_key=True)
    value = models.IntegerField(default= 0)
    percentile = models.FloatField(default= 0)
    source = models.CharField(max_length=200)
    interval = models.CharField(max_length=200)

    data_id = models.ForeignKey(Data_Set, on_delete=models.CASCADE)
    c_fips = models.ForeignKey(US_States, on_delete=models.CASCADE)
