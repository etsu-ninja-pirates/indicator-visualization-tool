import datetime
from django.db import models

# Create your models here.
class Indicators(models. Model):
    indicator_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    
class Data_Set(models.Model):
    data_id = models.BigIntegerField(primary_key=True)
    year = models.DateField()
    auther = models.CharField(max_length=200)
    
    indicator_id = models.ForeignKey(Indicators, on_delete=models.CASCADE)

class US_States(models.Model): 
    state_id = models.BigIntegerField(primary_key=True)
    short_name = models.CharField(max_length=200)
    state_name = models.CharField(max_length=200)
    s_fips = models.BigIntegerField(default = 0)

class US_Counties(models.Model):
    county_id = models.BigIntegerField(primary_key=True)
    county_name = models.CharField(max_length=200)
    c_fips = models.IntegerField()

    state_id = models.ForeignKey(US_States, on_delete=models.CASCADE)

class Data_Point(models.Model):
    point_id = models.BigIntegerField(primary_key=True)
    value = models.IntegerField(default= 0)
    precentile = models.FloatField(default= 0)
    source = models.CharField(max_length=200)
    interval = models.CharField(max_length=200)

    data_id = models.ForeignKey(Data_Set, on_delete=models.CASCADE)
    county_id = models.ForeignKey(US_States, on_delete=models.CASCADE)
