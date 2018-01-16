from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import HttpResponse
from django.http import Http404
from django.shortcuts import render
from django.shortcuts import render_to_response
from  django.template import RequestContext
import requests
from models import yearofdata,region_data,typeoftemp,raw_data
from django.views.decorators.csrf import csrf_exempt
import simplejson as json
#import reportsummary as rptlib



import logging
import simplejson as json
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
from django.shortcuts import HttpResponse
import datetime as dt
from datetime import datetime
import time
import os
import csv
from collections import OrderedDict		
#pg_pool = pg_obj.pool

def get_barchart_data():
	temp_type="Tmax"
	tempinfo=typeoftemp.objects.get(name__exact=temp_type)
	regioninfo=region_data.objects.get(name__exact='UK')
	#yearinfo=yearofdata.objects.get(name__exact=year)
	print "**************amol************************"
	#amol=raw_data.objects.filter(region=regioninfo,temp_type=tempinfo).only("y_data","JAN").order_by('-JAN')
	amol=raw_data.objects.filter(region=regioninfo,temp_type=tempinfo)
	

get_barchart_data()