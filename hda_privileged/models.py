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
    state = models.ForeignKey(US_State, related_name='state_id', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.fips + ' - '+ self.name +' - '+ self.state



# class US_States(models.Model): 
#     # state_id = models.BigIntegerField(primary_key=True)
#     abbreviation = models.CharField(primary_key=True, max_length=2)
#     state_name = models.CharField(max_length=20)
#     s_fips = models.CharField(max_length=2, default="")
    
#     def __str__(self):
#         return "%s  -  %s - %s" %(self.s_fips, self.abbreviation, self.state_name)

# class US_Counties(models.Model):
#     s_fips = models.CharField(max_length=2)
#     abbreviation = models.ForeignKey(US_States, on_delete=models.CASCADE, null=True, blank=True)
#     county_name = models.CharField(max_length=200)
#     c_fips = models.CharField(primary_key=True, max_length=3,default="")

    # def __str__(self):
    #     return "%s -  %s - %s - %s" % (self.c_fips, self.county_name, self.abbreviation, self.s_fips)

# class Data_Point(models.Model):
#     point_id = models.BigIntegerField(primary_key=True)
#     value = models.IntegerField(default= 0)
#     percentile = models.FloatField(default= 0)
#     source = models.CharField(max_length=200)
#     interval = models.CharField(max_length=200)

#     data_id = models.ForeignKey(Data_Set, on_delete=models.CASCADE)
    # c_fips = models.ForeignKey(US_States, on_delete=models.CASCADE)
