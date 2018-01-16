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
import sys

def index(request):
        if yearofdata.objects.count()==0 or region_data.objects.count()==0 or typeoftemp.objects.count()==0:
        	data=Loop_file_to_donload()	
        return render_to_response('reportsummary.html', context_instance=RequestContext(request))
   
    
@csrf_exempt
def Check_Data_From_Web(request):
	result=Loop_file_to_donload()
	return HttpResponse(json.dumps(result),content_type = "application/json")
	
def Loop_file_to_donload():
	
	try:
		fopen=open("region_info.txt","r")
		for fname in fopen:
			print "loading data from:",fname
			region=fname.split('/')[-1].split('.')[0]
			temp_type=fname.split('/')[-3]	
			process_file(region,temp_type,fname)
		fopen.close()
		result={'Status':'Success','msg':'Data Loaded Successfully'}
	except Exception,ex:
		result={'Status':'Error','msg':'Error in Data Loading'}
	return result
	
	
def process_file(region,temp_type,fname):
	r = requests.get(fname.strip(), stream=True)
	
	flag=0
	for line in r.iter_lines():
		if line:
			if 'Year    JAN    FEB    MAR    APR    MAY    JUN    JUL    AUG    SEP    OCT    NOV    DEC     WIN    SPR    SUM    AUT     ANN' in line:
				flag=1
				continue
			if flag:
				temp_list=line.strip().replace("---","0").split()
				year=temp_list[0]
				if(not yearofdata.objects.filter(name__exact=year).exists()):
					t = yearofdata(name = year)
					t.save()
				if(not region_data.objects.filter(name__exact=region).exists()):
					t = region_data(name = region)
					t.save()
				if(not typeoftemp.objects.filter(name__exact=temp_type).exists()):
					t = typeoftemp(name = temp_type)
					t.save()
				tempinfo=typeoftemp.objects.get(name__exact=temp_type)
				regioninfo=region_data.objects.get(name__exact=region)
				yearinfo=yearofdata.objects.get(name__exact=year)
				if (not raw_data.objects.filter(region=regioninfo,y_data=yearinfo,temp_type=tempinfo)):
					t=raw_data(
							region = regioninfo,
							y_data = yearinfo,
							temp_type = tempinfo,
							JAN= temp_list[1],
							FEB= temp_list[2],
							MAR= temp_list[3],
							APR= temp_list[4],
							MAY= temp_list[5],
							JUN= temp_list[6],
							JUL= temp_list[7],
							AUG= temp_list[8],
							SEP= temp_list[9],
							OCT= temp_list[10],
							NOV= temp_list[11],
							DEC= temp_list[12],
							WIN= temp_list[13],
							SPR= temp_list[14],
							SUM= temp_list[15],
							AUT= temp_list[16],
							ANN= temp_list[17]
						)
					t.save()
				
	
				
@csrf_exempt
def get_top_info(request):

	try:
		tempTransList = region_data.objects.filter()
		TransList=[]
		TransList1=[]
		result={}
		for tempTrans in tempTransList:
			TransList.append(tempTrans.name)
		tempTransList = typeoftemp.objects.filter()
		
		for tempTrans in tempTransList:
			TransList1.append(tempTrans.name)
		temp_dict={'temp_type':TransList1,'region':TransList}
		result['Status'] = "SUCCESS"
		result['data'] = temp_dict
	except Exception,e:
		print "ERROR:%s",str(e)
	return HttpResponse(json.dumps(result),content_type = "application/json")

def get_barchart_data(transName,reportName,re_type,measure):
	print "re_type=",re_type
	print "transName-",transName
	print "reportName-",reportName
	temp_type=reportName
	region=transName.upper()
	tempinfo=typeoftemp.objects.get(name__iexact=temp_type)
	regioninfo=region_data.objects.get(name__iexact=region)
	if re_type=='all':
		result_data=raw_data.objects.filter(region=regioninfo,temp_type=tempinfo).order_by('-JAN')[:10]
		
		temp_list=[]
		for a in result_data:
			temp_dict={}
			temp_dict['key']=a.y_data.name
			temp_dict['value']=a.JAN
			temp_list.append(temp_dict)
			temp_list1=[]
		result_data=raw_data.objects.filter(region=regioninfo,temp_type=tempinfo).order_by('-JAN')
		for a in result_data:
			temp_dict={}
			temp_dict['YEAR']=a.y_data.name
			temp_dict['JAN']=a.JAN
			temp_dict['FEB']=a.FEB
			temp_dict['MAR']=a.MAR
			temp_dict['APR']=a.APR
			temp_dict['MAY']=a.MAY
			temp_dict['JUN']=a.JUN
			temp_dict['JUL']=a.JUL
			temp_dict['AUG']=a.AUG
			temp_dict['SEP']=a.SEP
			temp_dict['OCT']=a.OCT
			temp_dict['NOV']=a.NOV
			temp_dict['DEC']=a.DEC
			temp_dict['WIN']=a.WIN
			temp_dict['SPR']=a.SPR
			temp_dict['SUM']=a.SUM
			temp_dict['AUT']=a.AUT
			temp_dict['ANN']=a.ANN
			temp_list1.append(temp_dict)
			
		pie_chart_data={'data':{'table':{'Status':'Success','Config':{'field_1':"JAN"},"Data":temp_list1},'pie':{'Status':'Success','Config':{'field_1':"JAN"},"Data":temp_list},'bar':{'Status':'Success','Config':{'field_1':"JAN"},"Data":temp_list},'line':{'Status':'Success','Config':{'field_1':"JAN"},"Data":temp_list}},'Status':'Success'}
		return pie_chart_data
	else:
		result_data=raw_data.objects.filter(region=regioninfo,temp_type=tempinfo).order_by('-'+measure)[:10]
		
		temp_list=[]
		for a in result_data:
			temp_dict={}
			temp_dict['key']=a.y_data.name
			if measure=="JAN":
				temp_dict['value']=a.JAN
			elif measure=="FEB":
				temp_dict['value']=a.FEB
			elif measure=="MAR":
				temp_dict['value']=a.MAR
			elif measure=="APR":
				temp_dict['value']=a.APR
			elif measure=="MAY":
				temp_dict['value']=a.MAY
			elif measure=="JUN":
				temp_dict['value']=a.JUN
			elif measure=="JUL":
				temp_dict['value']=a.JUL
			elif measure=="AUG":
				temp_dict['value']=a.AUG
			elif measure=="SEP":
				temp_dict['value']=a.SEP
			elif measure=="OCT":
				temp_dict['value']=a.OCT
			elif measure=="NOV":
				temp_dict['value']=a.NOV
			elif measure=="DEC":
				temp_dict['value']=a.DEC
			elif measure=="WIN":
				temp_dict['value']=a.WIN
			elif measure=="SPR":
				temp_dict['value']=a.SPR
			elif measure=="SUM":
				temp_dict['value']=a.SUM
			elif measure=="AUT":
				temp_dict['value']=a.AUT
			elif measure=="ANN":
				temp_dict['value']=a.ANN
			temp_list.append(temp_dict)
		measure=measure.upper()
		pie_chart_data={'data':{'pie':{'Status':'Success','Config':{'field_1':measure},"Data":temp_list},'bar':{'Status':'Success','Config':{'field_1':measure},"Data":temp_list},'line':{'Status':'Success','Config':{'field_1':measure},"Data":temp_list}},'Status':'Success'}
		return pie_chart_data

	
@csrf_exempt
def get_reportsummary_data(request):
	transName = request.POST.get('transName').lower()
	reportName = request.POST.get('reportName')
	re_type = request.POST.get('type')
	measure = request.POST.get('measure')
	response_data=get_barchart_data(transName,reportName,re_type,measure)
	return HttpResponse(json.dumps(response_data), content_type="application/json")
