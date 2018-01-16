from __future__ import unicode_literals
from django.db import models


class yearofdata(models.Model):
    name = models.CharField(max_length=64,null=False,blank=False,unique=True)
    
class region_data(models.Model):
    name = models.CharField(max_length=64,null=False,blank=False,unique=True)
    
class typeoftemp(models.Model):
    name = models.CharField(max_length=64,null=False,blank=False,unique=True)

class raw_data(models.Model):
    region = models.ForeignKey(region_data)
    y_data = models.ForeignKey(yearofdata)
    temp_type = models.ForeignKey(typeoftemp)
    JAN= models.FloatField()
    FEB= models.FloatField()
    MAR= models.FloatField()
    APR= models.FloatField()
    MAY= models.FloatField()
    JUN= models.FloatField()
    JUL= models.FloatField()
    AUG= models.FloatField()
    SEP= models.FloatField()
    OCT= models.FloatField()
    NOV= models.FloatField()
    DEC= models.FloatField()
    WIN= models.FloatField()
    SPR= models.FloatField()
    SUM= models.FloatField()
    AUT= models.FloatField()
    ANN= models.FloatField()
    
   