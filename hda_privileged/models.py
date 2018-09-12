import datetime
from django.db import models

# Create your models here.
# class Indicators(models. Model):
#     indicator_id = models.BigIntegerField(primary_key=True)
#     name = models.CharField(max_length=200)
    
# class Data_Set(models.Model):
#     data_id = models.BigIntegerField(primary_key=True)
#     year = models.DateField()
#     author = models.CharField(max_length=200)
    
#     indicator_id = models.ForeignKey(Indicators, on_delete=models.CASCADE)


class US_State(models.Model):
    short = models.CharField(primary_key=True, max_length=2)
    full = models.CharField(max_length=100)
    # Char instead of int because, like a phone number, we don't want to truncate leading zeros!
    fips = models.CharField(max_length=2)
    
    def __str__(self):
        return self.fips + ' - '+ self.short +' - '+ self.full

class US_County(models.Model):
    fips = models.CharField(max_length=3)
    name = models.CharField(max_length=200)
    state = models.ForeignKey(US_State, related_name='counties', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.fips + ' - '+ self.name +' - '+ self.state_id