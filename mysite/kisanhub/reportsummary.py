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
from settings import pg_obj
import os
import csv
from collections import OrderedDict		
logger = logging.getLogger('techlineage')
pg_pool = pg_obj.pool

def get_ReportSummaryStatus(transName,reportName):
    logger.info("get_ReportSummaryStatus: Getting Report Status")
    conn = None
    try:
        conn = pg_pool.getconn()
        cur = conn.cursor()
        reportName = reportName.lower()
        transName = transName.lower()
        cur.execute ("select 1 from information_schema.tables where table_name = '" + transName + "_" + reportName + "';")
        resultset =int((cur.fetchone())[0])
        cur.close()
        logger.info("get_ReportSummaryStatus: Report Count %s",resultset)
        if resultset == 1:
            logger.info("get_ReportSummaryStatus: Report Table \'%s\' Exists",reportName)
            return 1
        else:
            logger.info("get_ReportSummaryStatus: Report Table \'%s\' Does Not Exists",reportName)
            return 0
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        logger.error("Database Error get_ReportSummaryStatus!\n ->%s",exceptionValue)
    finally:
        if conn != None:
            pg_pool.putconn(conn)

def get_ReportSummaryConfig(transName,reportName,chartType):
    logger.info("get_ReportSummaryConfig Preparing query for chart: %s", chartType)
    resultset = {}
    conn = None
    try:
        conn = pg_pool.getconn()
        cur = conn.cursor()
        reportName = reportName.lower()
        query = "SELECT rc.* from app_report_chart_config as rc,app_chart_type as c,application_transformerdefinition as w,app_workspace_reports as wr where wr.w_id = w.id and rc.report_id = wr.id and rc.chart_id = c.id and w.name=\'"+transName.upper()+"\' and wr.report_name=\'"+reportName+"\' and c.chart_name=\'"+chartType+"\';"
        cur.execute (query)
        resultset[0] = cur.fetchone()
        if resultset[0]==None:
            logger.info("charttype not configured: %s", chartType)
            return None
        logger.info(resultset[0])
        cur1 = conn.cursor(cursor_factory=RealDictCursor)
        query = "SELECT rc.* from app_report_chart_config as rc,app_chart_type as c,application_transformerdefinition as w,app_workspace_reports as wr where wr.w_id = w.id and rc.report_id = wr.id and rc.chart_id = c.id and w.name=\'"+transName.upper()+"\' and wr.report_name=\'"+reportName+"\' and c.chart_name=\'"+chartType+"\';"
        cur1.execute (query)
        resultset[1] = cur1.fetchone()
        resultset[1]['created_on'] = int(time.mktime(resultset[1]['created_on'].timetuple()))
        resultset[1]['modified_on'] = int(time.mktime(resultset[1]['modified_on'].timetuple()))
        logger.info(resultset[1])
        logger.info("get_ReportSummaryConfig prepared")
        return resultset[1]
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        logger.info("Database Error get_ReportSummaryConfig!\n ->%s",exceptionValue)
    finally:
        if conn != None:
            pg_pool.putconn(conn)


def get_ReportSummaryQueryFilterStr(db_conn, reportName, workspaceName, conditions, advConditions):
    #get the report column definitions so that we know how the filtering will work
    report_column_dict = {}
    cur = db_conn.cursor()
    reportName = reportName.lower()
    workspaceName = workspaceName.upper()
    query = "SELECT awr.report_columns from app_workspace_reports awr, application_transformerdefinition atd where awr.w_id = atd.id and atd.name=\'"+workspaceName+"\' and awr.report_name=\'"+reportName+"\';"
    cur.execute(query)
    resultset = cur.fetchone()

    if resultset[0]==None:
        logger.info("Report columns are not configured")
    else:
        logger.info(resultset[0])
        report_column_dict = resultset[0]

    cur.close()
    complete_query_filter_str = ""

    for column in conditions.keys():
        if advConditions.has_key(column):
            logger.info("Skipping advfilter column:%s", column) 
            continue

        column_data_type = "text"
        query_str = ""

        if report_column_dict.has_key(column):
            column_info = report_column_dict[column]
            column_data_type = column_info[0].lower()

        if column_data_type == "datetime":
            logger.info("Skipping datetime column:%s", column) 
            continue

        cdn_value_list = conditions[column].keys()
        logger.info("Column: %s cdn_value_list: %s", column, str(cdn_value_list))

        if column_data_type == "text":
            if len(cdn_value_list) == 1:
                query_str = " and \"" + column + "\" = " + cdn_value_list[0] + " "
            else:
                query_str = " and \"" + column + "\" in (" + ",".join(cdn_value_list) + ") "
        else:
            if len(cdn_value_list) == 1:
                query_str = " and \"" + column + "\" = " + cdn_value_list[0] + " "
            else:
                query_str = " and \"" + column + "\" in (" + ",".join(cdn_value_list) + ") "

        logger.info("Column: %s QueryStr: %s", column, query_str)

        if len(complete_query_filter_str) > 0:
            complete_query_filter_str += query_str 
        else:
            complete_query_filter_str = query_str 

    for column in advConditions.keys():
        column_data_type = "text"
        query_str = ""

        if report_column_dict.has_key(column):
            column_info = report_column_dict[column]
            column_data_type = column_info[0].lower()

        if column_data_type == "datetime":
            continue

        cdn_value = advConditions[column]

        if column_data_type == "text":
            query_str = " and \"" + column + "\" like '%%" + cdn_value + "%%' "
        else:
            query_str = " and \"" + column + "\" = " + cdn_value + " "

        logger.info("Column: %s QueryStr: %s", column, query_str)

        if len(complete_query_filter_str) > 0:
            complete_query_filter_str += query_str 
        else:
            complete_query_filter_str = query_str

    logger.info("CompleteQueryStr: %s", complete_query_filter_str)
	
    return complete_query_filter_str


def get_ReportSummaryQuery(transName,reportName,startDate,endDate,cdn,pageValue,recordsPerPage,chartType,tl_hist_id):
    logger.info("get_ReportSummaryQuery Preparing query for charType: %s", chartType)
    query = {}
    conn = None
    start = 0
    reportName = reportName.lower()
    conn = pg_pool.getconn()
    cur = conn.cursor()
    to_date_format = 'YYYY-MM-DD HH24:MI:SS'
    try:
        if tl_hist_id != "" and tl_hist_id != None:
            hist_id_cdn = "tl_hist_id = " + str(tl_hist_id) + " and "
        else:
            hist_id_cdn = "tl_status = 'current' and "
    
        query_config = get_ReportSummaryConfig(transName,reportName,chartType)
        if query_config==None:
            return None

        logger.info("query_config=%s",query_config)
        reportName = transName.lower() + "_" + reportName

        if chartType == "pie":
            if query_config["order_by"] == "":
                query["data"] = "SELECT \""+query_config['field_1']+"\" as key,"+query_config['operation']+"(\""+query_config['field_2']+"\") as value FROM "+reportName+" as rp WHERE " + hist_id_cdn + " \""+query_config['field_3']+"\" >= TO_TIMESTAMP(\'"+startDate+"\','" + to_date_format + "') and \""+query_config['field_3']+"\" <= TO_TIMESTAMP(\'"+endDate+"\','" + to_date_format + "') "+cdn+"  group by \""+query_config['group_by']+"\" limit 10;"
                logger.info(query["data"])
            else:
                if query_config['order_by'] == query_config['field_2']:
                    ordby = query_config['operation']+"(\""+query_config['order_by']+"\")"
                else:
                    ordby = "\""+query_config['order_by']+"\""
                query["data"] = "SELECT \""+query_config['field_1']+"\" as key,"+query_config['operation']+"(\""+query_config['field_2']+"\") as value FROM "+reportName+" as rp WHERE " + hist_id_cdn + " \""+query_config['field_3']+"\" >= TO_TIMESTAMP(\'"+startDate+"\','" + to_date_format + "') and \""+query_config['field_3']+"\" <= TO_TIMESTAMP(\'"+endDate+"\','" + to_date_format + "') "+cdn+"  group by \""+query_config['group_by']+"\" order by " + ordby + " "+query_config['sort_order']+" limit 10;"
            logger.info(query["data"])
            query["config"] = query_config
        elif chartType == "bar":
            if query_config["order_by"] == "":
                query["data"] = "SELECT \""+query_config['field_1']+"\" as key,"+query_config['operation']+"(\""+query_config['field_2']+"\") as value FROM "+reportName+" as rp WHERE " + hist_id_cdn + " \""+query_config['field_3']+"\" >= TO_TIMESTAMP(\'"+startDate+"\','" + to_date_format + "') and \""+query_config['field_3']+"\"::date <= TO_TIMESTAMP(\'"+endDate+"\','" + to_date_format + "') "+cdn+"  group by \""+query_config['group_by']+"\" limit 10;"
                logger.info(query["data"])
            else:
                if query_config['order_by'] == query_config['field_2']:
                    ordby = query_config['operation']+"(\""+query_config['order_by']+"\")"
                else:
                    ordby = "\""+query_config['order_by']+"\""
                query["data"] = "SELECT \""+query_config['field_1']+"\" as key,"+query_config['operation']+"(\""+query_config['field_2']+"\") as value FROM "+reportName+" as rp WHERE " + hist_id_cdn + " \""+query_config['field_3']+"\" >= TO_TIMESTAMP(\'"+startDate+"\','" + to_date_format + "') and \""+query_config['field_3']+"\" <= TO_TIMESTAMP(\'"+endDate+"\','" + to_date_format + "') "+cdn+"  group by \""+query_config['group_by']+"\" order by value " +query_config['sort_order']+" limit 10;"
            logger.info(query["data"])
            query["config"] = query_config
        elif chartType == "line":
            columnTypeQuery = "select column_name, data_type from information_schema.columns where table_name = '" + reportName + "' and column_name='" + query_config['field_1'] + "';"
            cur.execute(columnTypeQuery)
            columnType_str = cur.fetchone()
            if columnType_str[1] == "timestamp without time zone":
                query_config['field_1'] = "CAST(\"" + query_config['field_1'] + "\" AS DATE)"
            else:
                query_config['field_1'] = "\"" + query_config['field_1'] + "\""
            columnTypeQuery = "select column_name, data_type from information_schema.columns where table_name = '" + reportName + "' and column_name='" + query_config['group_by'] + "';"
            cur.execute(columnTypeQuery)
            columnType_str = cur.fetchone()
            if columnType_str[1] == "timestamp without time zone":
                query_config['group_by'] = "CAST(\"" + query_config['group_by'] + "\" AS DATE)"
            else:
                query_config['group_by'] = "\"" + query_config['group_by'] + "\""            
            if query_config["order_by"] == "":
                query["data"] = "SELECT "+query_config['field_1']+" as key,"+query_config['operation']+"(\""+query_config['field_2']+"\") as value FROM "+reportName+" as rp WHERE " + hist_id_cdn + " \""+query_config['field_3']+"\" >= TO_TIMESTAMP(\'"+startDate+"\','" + to_date_format + "') and \""+query_config['field_3']+"\" <= TO_TIMESTAMP(\'"+endDate+"\','" + to_date_format + "') "+cdn+"  group by "+query_config['group_by']+" limit 10;"
            else:
                ordby = "CAST(\"" + query_config['order_by'] + "\" AS DATE)"
                query["data"] = "SELECT "+query_config['field_1']+" as key,"+query_config['operation']+"(\""+query_config['field_2']+"\") as value FROM "+reportName+" as rp WHERE " + hist_id_cdn + " \""+query_config['field_3']+"\" >= TO_TIMESTAMP(\'"+startDate+"\','" + to_date_format + "') and \""+query_config['field_3']+"\" <= TO_TIMESTAMP(\'"+endDate+"\','" + to_date_format + "') "+cdn+"  group by "+query_config['group_by']+" order by key "+query_config['sort_order']+" limit 10;"                
            logger.info(query["data"])
            query["config"] = query_config
        elif chartType == "table":
            start = (int(pageValue) - 1) * int(recordsPerPage)
            query["config"] = query_config
            
            sub_query = 'SELECT \'SELECT \' || array_to_string(ARRAY(SELECT \'"\' || c.column_name || \'"\' FROM information_schema.columns As c WHERE table_name = \'' + reportName + '\' AND  c.column_name NOT IN(\'created_by\', \'created_on\',\'modified_by\',\'modified_on\',\'id\',\'tl_hist_id\',\'tl_status\') ), \',\') || \' FROM ' + reportName + '\''
            cur.execute(sub_query)
            sub_query_str = cur.fetchone()
            
            query["data"] = sub_query_str[0] + " WHERE " + hist_id_cdn + " \""+query_config['field_3']+"\" >= TO_TIMESTAMP(\'"+startDate+"\','" + to_date_format + "') and \""+query_config['field_3']+"\" <= TO_TIMESTAMP(\'"+endDate+"\','" + to_date_format + "') "+cdn+" order by tl_hist_id DESC,\""+  query_config['field_3'] + "\" DESC limit "+str(recordsPerPage)+" offset "+str(start)+";"

            query["data_count"] = "SELECT count(rp.*) FROM "+reportName+" as rp WHERE " + hist_id_cdn + " \""+query_config['field_3']+"\" >= TO_TIMESTAMP(\'"+startDate+"\','" + to_date_format + "') and \""+query_config['field_3']+"\" <= TO_TIMESTAMP(\'"+endDate+"\','" + to_date_format + "') "+cdn+";"

        logger.debug("get_ReportSummaryQuery query prepared")
        logger.debug("%s Query-- %s",str(chartType),str(query["data"]))
        return query
    
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        logger.info("Database Error get_ReportSummaryQuery!\n ->%s",exceptionValue)
    finally:
            if conn != None:
                pg_pool.putconn(conn)
        
@csrf_exempt
@login_required
def get_PieChart_Data(request):
    logger.info("get_PieChart_Data")
    transName = request.POST.get('transName').lower()
    reportName = request.POST.get('reportName')
    startDate = request.POST.get('startDate')
    endDate = request.POST.get('endDate')
    conditions = request.POST.get('conditions')
    tl_hist_id = request.POST.get('reportId',None)
    
    #tl_hist_id = None
    
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
    startDate = time.strftime(TIMESTAMP_FORMAT, time.localtime(int(startDate)))
    endDate = time.strftime(TIMESTAMP_FORMAT, time.localtime(int(endDate)))
    
    reportName = reportName.lower()
    resultx = {}
    report_status = 0;
    query = {}
    query_data = ""
    conn = None
    try:
        report_status = get_ReportSummaryStatus(transName,reportName)
        if report_status == 1:
            conn = pg_pool.getconn()
            cur_cf = conn.cursor(cursor_factory=RealDictCursor)

            query = get_ReportSummaryQuery(transName,reportName,startDate,endDate,conditions,0,0,'pie',tl_hist_id)
            logger.info("get_ReportSummaryQuery query: %s", query)
            query_data = ()
            if query==None:
                resultx['Status'] = 'Error'
                resultx['Data'] = 'Chart is Not Defined'
            else:
                cur_cf.execute (query["data"],query_data)
                resultset =cur_cf.fetchall()
                logger.info(resultset)
                resultx['Status'] = 'Success'
                resultx['Data'] = resultset
                resultx['Config'] = query["config"]
        else:
            resultx['Status'] = 'Error'
            resultx['Data'] = 'Report Data does not exist'

        return HttpResponse(json.dumps(resultx), content_type="application/json")
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        logger.info("Database Server Error!\n ->%s",exceptionValue)
    finally:
        if conn != None:
            pg_pool.putconn(conn)

@csrf_exempt
@login_required
def get_BarChart_Data(request):
    logger.info("get_BarChart_Data")
    transName = request.POST.get('transName').lower()
    reportName = request.POST.get('reportName')
    startDate = request.POST.get('startDate')
    endDate = request.POST.get('endDate')
    conditions = request.POST.get('conditions')
    tl_hist_id = request.POST.get('reportId',None)
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
    startDate = time.strftime(TIMESTAMP_FORMAT, time.localtime(int(startDate)))
    endDate = time.strftime(TIMESTAMP_FORMAT, time.localtime(int(endDate)))
    
    reportName = reportName.lower()
    resultx = {}
    report_status = 0;
    query = {}
    query_data = ""
    conn = None
    try:
        report_status = get_ReportSummaryStatus(transName,reportName)
        if report_status == 1:
            conn = pg_pool.getconn()
            cur_cf = conn.cursor(cursor_factory=RealDictCursor)
            
            query = get_ReportSummaryQuery(transName,reportName,startDate,endDate,conditions,0,0,'bar',tl_hist_id)
            logger.info("get_ReportSummaryQuery query: %s", query)
            if query==None:
                resultx['Status'] = 'Error'
                resultx['Data'] = 'Chart is Not Defined'
            else:    
                query_data = ()
            
                cur_cf.execute (query["data"],query_data)
                resultset =cur_cf.fetchall()

                resultx['Status'] = 'Success'
                resultx['Data'] = resultset
                resultx['Config'] = query["config"]
        else:
            resultx['Status'] = 'Error'
            resultx['Data'] = 'Report Data does not exist'

        return HttpResponse(json.dumps(resultx), content_type="application/json")
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        logger.info("Database Server Error!\n ->%s",exceptionValue)
    finally:
        if conn != None:
            pg_pool.putconn(conn)

@csrf_exempt
@login_required
def get_ServerChart_Data(request):
    logger.info("get_ServerChart_Data")
    transName = request.POST.get('transName').lower()
    reportName = request.POST.get('reportName')
    startDate = request.POST.get('startDate')
    endDate = request.POST.get('endDate')
    conditions = request.POST.get('conditions')
    tl_hist_id = request.POST.get('reportId',None)
    
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
    startDate = time.strftime(TIMESTAMP_FORMAT, time.localtime(int(startDate)))
    endDate = time.strftime(TIMESTAMP_FORMAT, time.localtime(int(endDate)))
    reportName = reportName.lower()
    resultx = {}
    report_status = 0;
    query = {}
    query_data = ""
    conn = None
    try:
        report_status = get_ReportSummaryStatus(transName,reportName)
        if report_status == 1:
            conn = pg_pool.getconn()
            cur_cf = conn.cursor(cursor_factory=RealDictCursor)
            
            query = get_ReportSummaryQuery(transName,reportName,startDate,endDate,conditions,0,0,'line',tl_hist_id)
            if query==None:
                resultx['Status'] = 'Error'
                resultx['Data'] = 'Chart is Not Defined'                
            else:
                query_data = ()
                cur_cf.execute (query["data"],query_data)
                resultset =cur_cf.fetchall()
                for indx,t_dict in enumerate(resultset):
                    if (type(resultset[indx]['key']) is datetime) or (type(resultset[indx]['key']) is dt.date):
                        resultset[indx]['key'] = str(resultset[indx]['key'])
                resultx['Status'] = 'Success'
                resultx['Data'] = resultset
                resultx['Config'] = query["config"]
        else:
            resultx['Status'] = 'Error'
            resultx['Data'] = 'Report Data does not exist'

        return HttpResponse(json.dumps(resultx), content_type="application/json")
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        logger.info("Database Server Error!\n ->%s",exceptionValue)
    finally:
        if conn != None:
            pg_pool.putconn(conn)

@csrf_exempt
@login_required
def get_ReportSummary_Data(request):
    logger.info("get_ReportSummary_Data")
    transName = request.POST.get('transName').lower()
    reportName = request.POST.get('reportName')
    startDate = request.POST.get('startDate')
    endDate = request.POST.get('endDate')
    conditions = request.POST.get('conditions')
    pageValue = request.POST.get('pageValue')
    recordsPerPage = request.POST.get('recordsPerPage')
    tl_hist_id = request.POST.get('reportId',None)
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
    startDate = time.strftime(TIMESTAMP_FORMAT, time.localtime(int(startDate)))
    endDate = time.strftime(TIMESTAMP_FORMAT, time.localtime(int(endDate)))
    
    reportName = reportName.lower()
    resultx = {}
    report_status = 0;
    query = {}
    query_data = ""
    conn = None
    try:
        report_status = get_ReportSummaryStatus(transName,reportName)
        if report_status == 1:
            conn = pg_pool.getconn()
            cur_cf = conn.cursor(cursor_factory=RealDictCursor)

            query = get_ReportSummaryQuery(transName,reportName,startDate,endDate,conditions,pageValue,recordsPerPage,'table',tl_hist_id)
            logger.info("query: %s", query)
            if query==None:
                resultx['Status'] = 'Error'
                resultx['Data'] = 'Chart Not Defined'
            else:
                query_data = ()
                query_data1 = ()
            
                select_query = query["data"]
                #list_query = query_temp.split(' ',2)
                #logger.info("list_query: %s", str(list_query))
                #logger.info("list_query: %d", len(list_query))
                #temp_colList = list_query[1].split(',')
                #logger.info("temp_colList: %s", str(temp_colList))
                #list_query[1] = ''.join([col.split('.')[0] + '.\"' + col.split('.')[1].strip('"') + '\",' for col in temp_colList]).strip(',')
                #select_query = ' '.join(list_query)
                logger.info("select_query: %s %s", select_query, query_data)
                cur_cf.execute (select_query,query_data)
                resultset =json.dumps(cur_cf.fetchall(), default=datetimeEncodePostgres)
                logger.info("datacount_query: %s %s", query["data_count"], query_data1)
                cur_cf.execute (query["data_count"],query_data1)

                resultx['Status'] = 'Success'
                resultx['Data'] = json.loads(resultset)
                resultx['Data_Count'] = cur_cf.fetchall()
                resultx['Config'] = query["config"]
        else:
            resultx['Status'] = 'Error'
            resultx['Data'] = 'Report Data does not exist'

        return HttpResponse(json.dumps(resultx), content_type="application/json")
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        logger.info("Database Server Error!\n ->%s",exceptionValue)
    finally:
        if conn != None:
            pg_pool.putconn(conn)

def datetimeEncodePostgres(o):
   if isinstance(o, datetime):
      return o.isoformat()		

def getReportList(transformname, reportName = None):
    conn = None
    try:
        flag=0
        list_of_report=[]
        dict_of_id_to_report={}
        dict_of_report_chart={}
        conn = pg_pool.getconn()
        cur = conn.cursor()
        
        if reportName == None:
            cur.execute("SELECT awr.report_name,awr.id FROM app_workspace_reports awr,application_transformerdefinition aw WHERE aw.name=%(id)s and aw.id = awr.w_id" , {'id': transformname.upper()} )
        else:
            logger.info("executing query for report : %s", reportName) 
            cur.execute("SELECT awr.report_name,awr.id FROM app_workspace_reports awr,application_transformerdefinition aw WHERE aw.name=%(id)s and aw.id = awr.w_id and awr.report_name=%(rpt_name)s", {'id': transformname.upper(), 'rpt_name': reportName } )
        
        for list in cur.fetchall():
            list_of_report.append(list[0])
            dict_of_id_to_report[str(list[1])]=list[0]

        for report_id in dict_of_id_to_report:
            cur.execute("select upper(chart_name) from app_chart_type where id not in (select chart_id from app_report_chart_config where report_id=%(rid)s);",{"rid":report_id});
            list_of_chart=cur.fetchall()
            if list_of_chart==[]:
                dict_of_report_chart[dict_of_id_to_report[report_id]]=[]
            else:
                for list in list_of_chart:
                    if dict_of_id_to_report[report_id] in dict_of_report_chart:
                        dict_of_report_chart[dict_of_id_to_report[report_id]].append(list[0])
                    else:
                        dict_of_report_chart[dict_of_id_to_report[report_id]]=[list[0]]

        flag=1
    except Exception,ex:
        logger.error("getReportList Error!\n ->%s",ex)
        flag=0
    finally:
        if conn != None:
            pg_pool.putconn(conn)
    return dict_of_report_chart,list_of_report,flag

def getReportHeader(rpt_name,transName):
    conn = None
    try:
        conn = pg_pool.getconn()
        cur = conn.cursor()
        rpt_name = transName + "_" + rpt_name.lower()
        colnames = []
        datatypeList = []
        cur.execute("select column_name,data_type from information_schema.columns where table_schema =%(id)s and table_name=%(id1)s",{'id':'public','id1':rpt_name.lower()})
        for clist in cur.fetchall():
            datatypeList.append(clist[1])
            colnames.append(clist[0])

        return [colnames,datatypeList]
    except Exception,ex:
        logger.error("getReportHeader Error!\n ->%s",ex)
    finally:
        if conn != None:
            pg_pool.putconn(conn)

def InsertIntoDatabase(report_name,header,order,group,chart_type,asds,op_type,transName):
    conn = None
    report_name = report_name.lower()
    try:
        field=['','','','','','','','','','','','','','','','','']
        for idx, val in enumerate(header):
            try:
                field[idx]=val
            except Exception,ex:
                logger.info("InsertIntoDatabase Error!\n ->%s",ex)
        
        conn = pg_pool.getconn()
        cur = conn.cursor()
        
        chart_type=chart_type.lower()
        cur.execute("SELECT awr.id,act.id FROM app_workspace_reports awr,application_transformerdefinition aw, app_chart_type act WHERE awr.report_name=%(id)s and awr.w_id=aw.id  and aw.name=%(transName)s and act.chart_name=%(chart_type)s;", {'id': report_name,'transName':transName.upper(),'chart_type':chart_type} )     
        rep_chart_id = cur.fetchone()
        rpt_id=rep_chart_id[0]
        chart_id=rep_chart_id[1]

        if chart_type=='table':
            heading="None"
        else:
            heading=str(field[0])+" wise "+str(op_type)+" of "+str(field[1])
            heading=heading.lower()
        temp_dict={'report_id':rpt_id, 'chart_id':chart_id, 'field_1':str(field[0]), 'field_2':str(field[1]), 'field_3':str(field[2]), 'field_4':str(field[3]), 'field_5':str(field[4]), 'field_6':str(field[5]), 'field_7':str(field[6]), 'field_8':str(field[7]), 'chart_status':'TRUE', 'operation':op_type,'order_by':order, 'sort_order':asds, 'group_by':group, 'created_by':'postgres', 'created_on':str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'modified_by':'postgres','modified_on':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'chart_heading':heading}
        cur.execute("INSERT INTO public.app_report_chart_config(report_id, chart_id, field_1, field_2, field_3, field_4, field_5, field_6, field_7, field_8, chart_status, operation,order_by, sort_order, group_by, created_by, created_on, modified_by,modified_on,chart_heading)\
               VALUES (%(report_id)s, %(chart_id)s, %(field_1)s, %(field_2)s, %(field_3)s, %(field_4)s, %(field_5)s, %(field_6)s, %(field_7)s, %(field_8)s, %(chart_status)s, %(operation)s,%(order_by)s, %(sort_order)s, %(group_by)s, %(created_by)s, %(created_on)s, %(modified_by)s, %(modified_on)s,%(chart_heading)s)",temp_dict)
               
        conn.commit()
        return True
    except Exception,ex:
        logger.error("InsertIntoDatabase Error!\n ->%s",ex)
        conn.rollback()
        return False
    finally:
        if conn != None:
            pg_pool.putconn(conn)

def getReportChartConfigList(transformer_name, reportName):
    conn = None
    response_data = []        
    
    try:
        conn = pg_pool.getconn()
        cur = conn.cursor()
        transformer_name = transformer_name.lower()
        
        if reportName != None:
            report = reportName.lower()	    
            cur.execute("select chart_name,arcc.created_on,arcc.id,field_1,field_2,field_3,field_4,field_5,field_6,field_7,field_8,chart_status,operation,order_by,sort_order,group_by from app_report_chart_config arcc, app_workspace_reports awr, application_transformerdefinition aw, app_chart_type act where arcc.report_id=awr.id and arcc.chart_id = act.id and awr.w_id = aw.id and aw.name=%(transName)s and awr.report_name=%(rpt_name)s",{'rpt_name': report,'transName':transformer_name.upper()})
        else:
            cur.execute("select chart_name,arcc.created_on,arcc.id,field_1,field_2,field_3,field_4,field_5,field_6,field_7,field_8,chart_status,operation,order_by,sort_order,group_by from app_report_chart_config arcc, app_workspace_reports awr, application_transformerdefinition aw, app_chart_type act where arcc.report_id=awr.id and arcc.chart_id = act.id and awr.w_id = aw.id and aw.name=%(transName)s",{'transName':transformer_name.upper()})
        
        chart_info_dtls = cur.fetchall()
        
        for chart_info in chart_info_dtls:
            temp_dict={}            
            temp_dict['reportName']=report
            temp_dict['chart_name']=chart_info[0]
            temp_dict['createdTime']=str(chart_info[1].strftime("%a %d %B %Y %H:%M:%S"))
            temp_dict['chartconfig_id']=chart_info[2]
            temp_dict['field_1']=chart_info[3]
            temp_dict['field_2']=chart_info[4]
            temp_dict['field_3']=chart_info[5]
            temp_dict['field_4']=chart_info[6]
            temp_dict['field_5']=chart_info[7]
            temp_dict['field_6']=chart_info[8]
            temp_dict['field_7']=chart_info[9]
            temp_dict['field_8']=chart_info[10]
            temp_dict['chart_status']=chart_info[11]
            temp_dict['operation']=chart_info[12]
            temp_dict['order_by']=chart_info[13]
            temp_dict['sort_order']=chart_info[14]
            temp_dict['group_by']=chart_info[15]
            
            response_data.append(temp_dict)
    
    except Exception,ex:
        logger.error("getReportChartConfigList Error!\n ->%s",ex)
    finally:
        if conn != None:
            pg_pool.putconn(conn)
            
    logger.info("report_data: %s", response_data)
    return response_data    
        
def deleteReportChartConfig(trans,reportName,chart_type):
    conn = None
    reportName = reportName.lower()
    try:
        conn = pg_pool.getconn()
        cur = conn.cursor()
        
        logger.info("executing query_str")
        cur.execute("delete from app_report_chart_config where report_id in (select awr.id from app_workspace_reports awr, application_transformerdefinition aw where aw.id = awr.w_id and awr.report_name=%(rpt_name)s and aw.name=%(workspace_name)s) and chart_id in (select id from app_chart_type where chart_name=%(chart_type)s);",{"rpt_name":reportName.lower(),"workspace_name":trans.upper(),"chart_type":chart_type.lower()});  
        logger.info("executed query_str")
        #cur.execute("delete from app_report_chart_config arcc, app_workspace_reports awr, app_workspace aw, app_chart_type act WHERE awr.report_name=%(rpt_name)s and aw.workspace_name=%(trans_name) and act.chart_type=%(chart_name)s and aw.id = awr.w_id and arcc.report_id = awr.id and arcc.chart_id = act.id ", {'rpt_name': reportName.lower(),'trans_name':trans.lower(),'chart_name':chart_type.lower()})
        conn.commit()
        deleted=cur.statusmessage
        flag=1
    except Exception,ex:
        flag=0
        logger.error("deleteReportChartConfig Error!\n ->%s",ex)
        conn.rollback()
    finally:
        if conn != None:
            pg_pool.putconn(conn)
    return flag
    
def UpdateReportChart(report_name,header,order,group,chart_type,asds,op_type,report_id):
    conn = None
    report_name = report_name.lower()
    try:
        field=['','','','','','','','','','','','','','','','','']
        for idx, val in enumerate(header):
            try:
                field[idx]=val
            except Exception,ex:
                logger.error("UpdateReportChart Error!\n ->%s",ex)
        
        conn = pg_pool.getconn()
        cur = conn.cursor()
        temp_dict={'field_1':str(field[0]), 'field_2':str(field[1]), 'field_3':str(field[2]), 'field_4':str(field[3]), 'field_5':str(field[4]), 'field_6':str(field[5]), 'field_7':str(field[6]), 'field_8':str(field[7]), 'chart_status':'TRUE', 'operation':op_type,'order_by':order, 'sort_order':asds, 'group_by':group,'modified_on':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'report_id':report_id}
        cur.execute("Update public.app_report_chart_config set field_1=%(field_1)s,field_2=%(field_2)s, field_3=%(field_3)s, field_4=%(field_4)s, field_5=%(field_5)s, field_6=%(field_6)s, field_7=%(field_7)s, field_8=%(field_8)s, chart_status=%(chart_status)s, operation=%(operation)s,order_by=%(order_by)s, sort_order=%(sort_order)s, group_by=%(group_by)s, modified_on=%(modified_on)s where id=%(report_id)s",temp_dict)
        conn.commit()
        return True
    except Exception,ex:
        logger.error("UpdateReportChart Error!\n ->%s",ex)
        conn.rollback()
        return False
    finally:
        if conn != None:
            pg_pool.putconn(conn)
        
def getChartToAdd(dict_of_report_chart):
    conn = None
    try:
        list_of_chart=[]
        conn = pg_pool.getconn()
        cur = conn.cursor()
        cur.execute("SELECT chart_name FROM app_chart_type")
        list_of_chart_id_to_name=cur.fetchall()
        for chart in list_of_chart_id_to_name:
            list_of_chart.append(chart[0].upper())
            
        for key in dict_of_report_chart:
            temp_list=[]
            for chart_type in list_of_chart:
                if not chart_type in dict_of_report_chart[key]:
                    temp_list.append(chart_type)
            dict_of_report_chart[key]=temp_list
        return dict_of_report_chart    
    except Exception,ex:
        logger.error("getChartToAdd Error!\n ->%s",ex)
    finally:
        if conn != None:
            pg_pool.putconn(conn)

  
@csrf_exempt
@login_required
def getDatatypesList(request):
    conn = None
    try:
        resp_text = {}
        conn = pg_pool.getconn()
        cur = conn.cursor()
        cur.execute("SELECT datatype_alias from app_master_datatypes")
        resultset = cur.fetchall()
        resp_text['Status'] = "SUCCESS"
        resp_text['Data'] = []
        for item in resultset:
            resp_text['Data'].append(item[0])
    except Exception,ex:
        logger.error("Postgres Database Server Error!\n Failed To Fetch Datatype List \n ->%s",str(ex))
        resp_text['Status'] = "ERROR"
        resp_text['Data'] = "Failed to get datatypes exception " + str(ex)
    finally:
        if conn != None:
            pg_pool.putconn(conn)
    
    return HttpResponse(json.dumps(resp_text), content_type="application/json")
    

def updateTimetrend(conn, transName,reportName,dict_timeColumn):
    try:
        cur = conn.cursor()
        logger.debug("dict_timeColumn:%s", dict_timeColumn)
        cur.execute("SELECT awr.id FROM app_workspace_reports awr,application_transformerdefinition aw WHERE awr.report_name=%(reportName)s and awr.w_id=aw.id and aw.name=%(transName)s;", {'reportName': reportName,'transName':transName.upper()})
        rpt_id=cur.fetchone()[0]
        
        cur.execute("select id from app_chart_type where chart_name='line'")
        chart_id=cur.fetchone()[0]
        cur.execute("select 1 as temp_no from app_report_chart_config where report_id="+ str(rpt_id) +" and chart_id=" + str(chart_id) + ";")
        is_rec_present = cur.fetchone()
        field=['','','','','','','','','','','','','','','','','']
        order = ""
        asds = "ASC"
        op_type = "COUNT"
        group = ""
        if "Time" in dict_timeColumn:
            field=['Time','Time','Time','Time','','','','','','','','','','','','','']
            group = order = "Time"
        else:
            if len(dict_timeColumn) > 0:
                for temp_col in dict_timeColumn:
                    field=[temp_col,temp_col,temp_col,temp_col,'','','','','','','','','','','','','']
                    group = order = temp_col
                    break
            else:
                temp_col='created_on'
                field=[temp_col,temp_col,temp_col,temp_col,'','','','','','','','','','','','','']
                group = order = temp_col
        temp_dict={'report_id':rpt_id, 'chart_id':chart_id, 'field_1':str(field[0]), 'field_2':str(field[1]), 'field_3':str(field[2]), 'field_4':str(field[3]), 'field_5':str(field[4]), 'field_6':str(field[5]), 'field_7':str(field[6]), 'field_8':str(field[7]), 'chart_status':'TRUE', 'operation':op_type,'order_by':order, 'sort_order':asds, 'group_by':group, 'created_by':'postgres', 'created_on':str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'modified_by':'postgres','modified_on':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        if is_rec_present is not None:
            cur.execute("UPDATE public.app_report_chart_config SET field_1 = %(field_1)s, field_2 = %(field_2)s, field_3 = %(field_3)s, field_4 = %(field_4)s, field_5 = %(field_5)s, field_6 = %(field_6)s, field_7 = %(field_7)s, field_8 = %(field_8)s, chart_status = %(chart_status)s, operation = %(operation)s,order_by = %(order_by)s, sort_order = %(sort_order)s, group_by = %(group_by)s, modified_by = %(modified_by)s, modified_on = %(modified_on)s where chart_id = %(chart_id)s and report_id = %(report_id)s",temp_dict)
        else:
            cur.execute("INSERT INTO public.app_report_chart_config(report_id, chart_id, field_1, field_2, field_3, field_4, field_5, field_6, field_7, field_8, chart_status, operation,order_by, sort_order, group_by, created_by, created_on, modified_by,modified_on)\
            VALUES (%(report_id)s, %(chart_id)s, %(field_1)s, %(field_2)s, %(field_3)s, %(field_4)s, %(field_5)s, %(field_6)s, %(field_7)s, %(field_8)s, %(chart_status)s, %(operation)s,%(order_by)s, %(sort_order)s, %(group_by)s, %(created_by)s, %(created_on)s, %(modified_by)s, %(modified_on)s)",temp_dict)
        #columnTypeQuery = "select column_name, data_type from information_schema.columns where table_name = '" + reportName + "' and data_type='timestamp without time zone';"
        #cur.execute(columnTypeQuery)
        cur.close()
        return True
    except Exception,ex:
        logger.error("Error in updateTimetrend %s",str(ex))
        cur.close()
        return False
def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    same = set(o for o in intersect_keys if d1[o] == d2[o])
    return added, removed, modified, same

def createNewReportSummaryTable(transName,reportName,columnDict,reportDefn,type1):
    conn = None
    reportName = reportName.lower()
    logger.debug("Create new report name: %s type:%s column:%s defn:%s", reportName, type1, type(columnDict), type(reportDefn))
    isDropped = False
    table_header=['', '', 'created_on', 'created_on']
    try:
        resp_text = {}
        conn = pg_pool.getconn()
        cur = conn.cursor()
        workspace_id = ""
        try:
            workspace_id = getWorkspaceId(cur,transName)
        except Exception,ex:
            logger.info("Workspace not available")
            workspace_id = ""
        dict_timeColumn = {}
        if type1=='ADD_REPORT':
            addReportDefinition(cur, transName,reportName, columnDict, reportDefn)
        logger.info("columnDict: %s", columnDict)
        query = 'CREATE TABLE '+ transName.lower() + "_" + reportName +'(id serial PRIMARY KEY,'
        report_defn_dict={}
        report_col_dict={}
        columnDict1={}
        reportDefnDict1={}
        columnDict1=json.loads(columnDict)
        if type1=='MODIFY_REPORT':
            try:
                reportDefnDict1=reportDefn
                get_query="SELECT report_columns, report_definition FROM app_workspace_reports WHERE w_id=" + str(workspace_id) + " and report_name='" + reportName + "';"
                cur.execute(get_query)
                row = cur.fetchone()
                report_col_dict = row[0]
                report_defn_dict = row[1]
            except Exception,ex:
                logger.error("Error=>%s",ex)
                report_col_dict={}
                report_defn_dict = {}
        
        if type1=='MODIFY_REPORT' and cmp(report_col_dict,columnDict1)==0 and cmp(report_defn_dict,reportDefnDict1)==0: 
            logger.info("Unchanged Report Table For Modification->%s",reportName)
            resp_text['Status'] = "SUCCESS"
            resp_text['Data'] = "Table Exist"
            return resp_text
        elif (columnDict1 != {} and cmp(report_col_dict,columnDict1)!=0):
            dropReportSummaryTable(cur,transName,reportName)
            isDropped = True
            for key, value in json.loads(columnDict,object_pairs_hook=OrderedDict).iteritems():
                logger.debug("Key: %s Value; %s", key, value)
                if str(value[0]) == "datetime":
                    value[0] = "timestamp without time zone"
                    dict_timeColumn[key]=value[0]

                query += "\"" + str(key)+ "\" " + str(value[0])+ ","
        
            query += 'created_by text NOT NULL DEFAULT "current_user"(),created_on timestamp without time zone NOT NULL DEFAULT now(),modified_by text NOT NULL DEFAULT "current_user"(),modified_on timestamp without time zone NOT NULL DEFAULT now(),tl_hist_id integer,tl_status text);'
            try:
                logger.debug("Executing query: %s", query)
                cur.execute(query)
            except Exception,ex:
                logger.error("createNewReportSummaryTable error \n ->%s",ex)
        if type1=='MODIFY_REPORT':
            added = False
            update_query = 'UPDATE app_workspace_reports set '
            if cmp(report_col_dict,columnDict1)!=0:
                update_query = update_query + ' report_columns=\''+ str(columnDict).replace('\'','\"') +'\''
                added = True
            added1, removed, modified, same = dict_compare(report_defn_dict,reportDefn)
            logger.debug("%s %s %s %s => %s ", added1, removed, modified, len(modified),(len(modified) !=0 and (len(modified) != 1 and not modified.has_key('createdTime'))))
            if len(added1) !=0 or len(removed) != 0 or (len(modified) !=0 and not(len(modified) == 1 and modified.has_key('createdTime'))):
                logger.debug("%s old:%s new:%s", type(report_defn_dict),report_defn_dict, reportDefn)
                if added:
                    update_query = update_query + ","
                update_query = update_query + ' report_definition=\''+ json.dumps(reportDefn)+'\''
                added = True
            if added:
                update_query =  update_query + ' where w_id=' + str(workspace_id)+ ' and report_name=\'' + reportName + '\';'
                logger.info("Update query %s", update_query)
                cur.execute(update_query)
        resp_text['Status'] = "SUCCESS"
        resp_text['Data'] = ["Report Table Created Successfully"]
        cur.close()
        if updateTimetrend(conn, transName.lower(),reportName,dict_timeColumn) == True:
            conn.commit()
        else:
            conn.rollback()
        if isDropped and type1 != "ADD_REPORT":
            InsertIntoDatabase(reportName,table_header,'','','table','','',transName)
    except Exception,ex:
        logger.error("Postgres Database Server Error!\n Failed to create report table \n ->%s",str(ex))
        resp_text['Status'] = "ERROR"
        resp_text['Data'] = "Failed to create report table exception " +str(ex)
        conn.rollback()
    finally:
        if conn != None:
            pg_pool.putconn(conn)
    logger.debug("%s resp_text: %s", isDropped, resp_text)
    return resp_text

def deleteReportSummaryTable(transName,reportName):    
    conn = None
    reportName = reportName.lower()
    try:
        resp_text = {}
        conn = pg_pool.getconn()
        cur = conn.cursor()    
        dropReportSummaryTable(cur,transName,reportName)
        dropReportDefinitionTable(cur,transName,reportName)
        resp_text['Status'] = "SUCCESS"
        resp_text['Data'] = ["Report Table Deleted Successfully"]
        conn.commit()
    except Exception,ex:
        logger.info("Postgres Database Server Error!\n Failed To Fetch Datatype List \n ->%s",str(ex))
        resp_text['Status'] = "ERROR"
        resp_text['Data'] = "Failed to create report table exception " + str(ex)
        conn.rollback()
    finally:
        if conn != None:
            pg_pool.putconn(conn)

def addReportDefinition(cur, transName,reportName,columnDict,reportDefinition):
    logger.info("Adding new report %s %s %s", transName, reportName, reportDefinition)
    try:
        insert_query = "INSERT INTO app_workspace_reports(w_id,report_name,report_columns,report_definition) VALUES ((SELECT id FROM application_transformerdefinition WHERE name='%s'), '%s', '%s','%s');"%(transName.upper(),reportName,columnDict,json.dumps(reportDefinition))
        logger.debug("Insert query %s", insert_query)
        cur.execute(insert_query)
    except Exception,ex:
        logger.error("Failed to add the report %s",ex)

def dropReportDefinitionTable(cur,transName,reportName):
	logger.info("Deleting the report definition for %s %s", transName, reportName)
	try:
		reportName = reportName.lower()
		try:
			workspace_id = getWorkspaceId(cur,transName)
		except Exception,ex:
			logger.info("Workspace not available")
			workspace_id = ""
		try:
			report_id = getReportId(cur,workspace_id,reportName)
		except Exception,ex:
			logger.info("No Report Available ex:%s",ex)
			report_id = ""

		if report_id != "":
			cur.execute("DELETE FROM app_workspace_reports WHERE w_id=%(workspace_id)s and report_name=%(reportName)s;",{'reportName': reportName,'workspace_id': workspace_id })
	except Exception,ex:
		logger.error("Failed to delete the report %s",ex)

def dropReportSummaryTable(cur,transName,reportName):
    reportName = reportName.lower()
    try:
        workspace_id = getWorkspaceId(cur,transName)
    except Exception,ex:
        logger.info("Workspace not available")
        workspace_id = ""
    try:
        report_id = getReportId(cur,workspace_id,reportName)
    except Exception,ex:
        logger.info("No Report Available")
        report_id = ""
        
    if report_id != "":
        cur.execute("DELETE FROM app_report_chart_config WHERE report_id = %(report_id)s;", {'report_id': report_id })
        #cur.execute("DELETE FROM app_reporthistory WHERE report_id = %(report_id)s ;",{'report_id': report_id})
        #cur.execute("DELETE FROM app_workspace_reports WHERE w_id=%(workspace_id)s and report_name=%(reportName)s;",{'reportName': reportName,'workspace_id': workspace_id })
        cur.execute("DROP TABLE IF EXISTS "+ transName.lower() + "_" + reportName+";")
    

def getWorkspaceId(cur,transName):
    cur.execute("SELECT id FROM application_transformerdefinition WHERE name=%(transName)s;", {'transName': transName.upper() } )
    workspace_id=cur.fetchone()[0]
    logger.info("%s Workspace with id = %s",transName,workspace_id)
    return workspace_id

def getReportId(cur,workspace_id,reportName):
    reportName = reportName.lower()
    #workspace_id = getWorkspaceId(cur,transName)
    cur.execute("SELECT id FROM app_workspace_reports WHERE w_id=%(workspace_id)s and report_name=%(reportName)s;", {'reportName': reportName,'workspace_id': workspace_id } )
    report_id=cur.fetchone()[0]
    logger.info("Workspace with id = %s and report_id = %s",workspace_id,report_id)
    return report_id

def getAllReportSummaryTableSchema(transName):
    logger.info("getAllReportSummaryTableSchema start")
    conn = None
    try:
        resp_text = {}
        report_col_list_datatype = {}
        report_defn_list_datatype = {}
        conn = pg_pool.getconn()
        cur = conn.cursor()
        cur.execute("SELECT report_name, report_columns, report_definition FROM app_workspace_reports awr,application_transformerdefinition aw WHERE awr.w_id = aw.id and aw.name=%(transName)s;", {'transName': transName.upper() })
        resultset = cur.fetchall()
        for row in resultset:
            report_col_list_datatype[row[0]] = row[1]
            report_defn_list_datatype[row[0]] = row[2]
        resp_text["SchemaData"] = report_col_list_datatype
        resp_text["ReportDefinition"] = report_defn_list_datatype
        resp_text['Status'] = "SUCCESS"
        resp_text['Data'] = ["Report Table Created Successfully"]
        conn.commit()
    except Exception,ex:
        logger.info("Postgres Database Server Error!\n Failed to Get Report Table Schema \n ->%s",str(ex))
        resp_text['Status'] = "ERROR"
        resp_text['Data'] = "Failed to get report table schema exception " +str(ex)
        conn.rollback()
    finally:
        if conn != None:
            pg_pool.putconn(conn)

    return resp_text


def deleteWorkspace(transName,conn):
    try:
        resp_text = {}
        cur = conn.cursor()
        cur.execute("SELECT report_name FROM app_workspace_reports awr,application_transformerdefinition aw WHERE awr.w_id = aw.id and aw.name=%(transName)s;", {'transName': transName.upper()})
        resultset = cur.fetchall()
        logger.info("resultset:%s",resultset)
        for reportName in resultset:
            deleteReportSummaryTable(transName,reportName[0])
        
        resp_text['Status'] = "SUCCESS"
        resp_text['Data'] = ["Workspace Deleted Successfully"]
    except Exception,ex:
        logger.error("Postgres Database Server Error!\n Failed to delete Workspace \n ->%s",str(ex))
        resp_text['Status'] = "ERROR"
        resp_text['Data'] = "Failed to delete Workspace exception " + str(ex)
    return resp_text

def GetIndexesfor(first_line, dict_of_strings):
    ret = {}
    logger.debug("first_line--%s",str(first_line))
    list_of_strings = dict_of_strings.keys()
    for i in range(len(list_of_strings)):
        if list_of_strings[i] in first_line:
            ret[first_line.index(list_of_strings[i])] = list_of_strings[i]
        else:
            ret = {}
            return ret
    return ret

def GetDatetimeColumns(reportName,trans_id,cur):
    try:
        timeColumnDict = {}
        selectQuery = "SELECT report_columns from app_workspace_reports where w_id=" + str(trans_id) + " and report_name='" + str(reportName) + "'"
        logger.debug("selectQuery--%s",selectQuery)
        cur.execute(selectQuery)
        report_columns = cur.fetchone()[0]
        logger.debug("report_columns--type - %s %s",type(report_columns),report_columns)
        for key, value in report_columns.items():
            if value[0] == "datetime":
                timeColumnDict[key] = value[1]
        logger.debug("timeColumnDict--%s",str(timeColumnDict))
        return timeColumnDict
    except Exception,e:
        logger.info("Error in GetDatetimeColumns-%s",str(e))

def convertTime(Time,currFormat):
    try:
        TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
        timestamp = int(time.mktime(time.strptime(Time,currFormat)))
        timestamp = time.strftime(TIMESTAMP_FORMAT, time.localtime(timestamp))
        return timestamp
    except Exception,e:
        logger.info("Error in convertTime-%s",str(e))
        return -1


def do_EnqueueReportUploadRequest(reportName, reportUploadRequest):
    try:
        conn = pg_pool.getconn()
        cur = conn.cursor()
        logger.info("Start Of the do_EnqueueReportUploadRequest Function")
        reportUploadRequestJson = json.dumps(reportUploadRequest)
        
        logger.info("Successfully Connected to Postgres Database")
        query = "INSERT INTO app_report_upload_request(report_name, report_details, status) values('" + reportName + "','" + reportUploadRequestJson + "','PENDING');"
        cur.execute(query);
        conn.commit()
    except Exception, ex:
	logger.error("Error in enqueuing report upload request: %s", str(ex))
    finally:
        cur.close()
        pg_pool.putconn(conn)
	
def do_PushDataIntoDatabase(reportData,REPORT_STORAGE_PATH):
    response_data = {}
    try:
        logger.debug("Start Of the do_PushDataIntoDatabase Function")
        conn = pg_pool.getconn()
        cur = conn.cursor()
        
        conn1 = pg_pool.getconn()
        cur1 = conn1.cursor()
        
        logger.debug("Successfully Connected to Postgres Database")
        StartTime = reportData.start_time
        EndTime = reportData.end_time
        logger.debug("Report Time Range = StartTime:%s and EndTime:%s",StartTime,EndTime)
        trans_id = reportData.transformer_id
        logger.debug("trans_id :%s",trans_id)
        execute_time = reportData.execution_start_time
        logger.debug("execute_time :%s",execute_time)
        rpt_file_name = reportData.filename
        logger.debug("rpt_file_name :%s",rpt_file_name)
        user = reportData.user_id
        logger.debug("user :%s",user)
        reportName = reportData.report_type
        logger.debug("reportName :%s",reportName)
        rpt_file_path = REPORT_STORAGE_PATH + rpt_file_name
        rpt_file_path = rpt_file_path.replace('\\','/')
        logger.debug("Report File Path :%s",rpt_file_path)
        rept_hist_id = reportData.id
        logger.debug("rept_hist_id :%s",str(rept_hist_id))
        
        cur.execute("SELECT wr.id as rid,ws.name as wname FROM app_workspace_reports as wr,application_transformerdefinition as ws WHERE wr.w_id=%(workspace_id)s and wr.report_name=%(reportName)s and wr.w_id=ws.id;", {'reportName': reportName,'workspace_id': trans_id })
        result = cur.fetchone()
        report_id = result[0]
        transName = result[1].lower()
        logger.debug("report_id--%s,transName--%s",str(report_id),str(transName))
        
        if os.path.isfile(rpt_file_path):
            logger.debug("File found")
            
            try:
                check_report_query = "select count(pt.*) from pg_tables as pt where pt.schemaname='public' and     pt.tablename='" + transName + "_" + reportName + "' union all select count(wr.*) from app_workspace_reports as wr where wr.w_id=" + str(trans_id) + " and wr.report_name = '" + reportName + "';"
                logger.debug("check_report_query-%s",str(check_report_query))
                cur.execute(check_report_query)
                resultset = cur.fetchall()
                if int(resultset[0][0]) == 0 and int(resultset[1][0]) == 1:
                    report_file=open(rpt_file_path,"r")
                    col_names = report_file.next()
                    logger.info("column name: %s", col_names)
                    report_file.close()
                    col_names = col_names.strip('\n')
                    col_names = col_names.split(',')
                    columnDict = {}
                    for col in col_names:
                        columnDict[col] = ["text",""]
                    logger.info("columndict: %s", columnDict)
                    create_query = 'CREATE TABLE '+ transName + "_" + reportName +'(id serial PRIMARY KEY,'
                    for key,value in columnDict.items():
                        create_query += "\"" + str(key)+ "\" " + str(value[0]) +","
                    
                    create_query += 'created_by text NOT NULL DEFAULT "current_user"(),created_on timestamp     without time zone NOT NULL DEFAULT now(),modified_by text NOT NULL DEFAULT "current_user"(),modified_on timestamp without time zone NOT NULL DEFAULT now(),tl_hist_id integer,tl_status text);'

                    logger.info("Create Query: %s", create_query)
                    
                    update_query = 'update app_workspace_reports set report_columns=\''+ str(columnDict).replace('\'','\"') +'\' where w_id=' + str(trans_id)+ ' and report_name=\'' + reportName + '\';'
                    logger.info("Update Query: %s", update_query)
                    try:
                        
                        cur1.execute(create_query)
                        cur1.execute(update_query)
                        conn1.commit()
                        logger.info("columnList \n ->%s",columnDict)
                    except Exception,ex:
                        logger.error("do_PushDataIntoDatabase error \n ->%s",ex)
            except Exception,e:
                logger.error("do_PushDataIntoDatabase error \n ->%s",e)
            
            query="select MAX(id) from "+ transName + "_" + str(reportName) +";"
            cur.execute(query)
            resultset = cur.fetchone()
            if resultset[0]==None or resultset[0]==0:
                sr=1
            else:
                sr=resultset[0]+1
            
            logger.debug("id %s",sr)
            logger.debug("resultset %s",resultset)
            file=open(rpt_file_path,"r")
            reader = csv.reader(file, delimiter=',', quotechar='"')
            myString = reader.next()
            
            dictDatetimeColumns = GetDatetimeColumns(reportName,trans_id,cur)
            logger.debug("dictDatetimeColumns--%s",str(dictDatetimeColumns))
            indexDatetime = GetIndexesfor(myString, dictDatetimeColumns)
            logger.debug("indexDatetime--%s",str(indexDatetime))
            
            myString = ["\"" + col + "\"" for col in myString]
            myString.append('"tl_status"')
            myString.append('"tl_hist_id"')
            headers = ",".join(myString)
            logger.info("Report Header is: %s",str(headers))
            logger.debug("headers,reportName,trans_id--%s %s %s",str(headers),str(reportName),str(trans_id))
            
            #UPDATE TO REPORT TABLE ON RECORDS OVERLAPPING
            timeCol = ''
            if dictDatetimeColumns != {}:
                DateTimeColumnList = dictDatetimeColumns.keys()
                timeIndex = [DateTimeColumnList.index(x) for x in DateTimeColumnList if x.lower() == 'time']
                if timeIndex != []:
                    timeCol = DateTimeColumnList[timeIndex[0]]
                else:
                    timeCol = dictDatetimeColumns.keys()[0]
            else:
                timeCol = "created_on"
            startTimeStr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(StartTime)))
            endTimeStr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(EndTime)))
            logger.debug("starttime=%s, endtime=%s",str(startTimeStr),str(endTimeStr))
            updateQuery = "UPDATE " + transName + "_" + reportName + " set tl_status='old' where \"" + timeCol + "\" >= '" + startTimeStr + "' and \"" + timeCol + "\" <= '" + endTimeStr + "'"
            logger.info("updateQuery = %s",str(updateQuery))
            cur.execute(updateQuery)
            lineCnt = 0
            for myString in reader:
                logger.info("myString : %s", myString)
                if len(myString) == 0:
                    logger.debug("Continuing due to empty line")
                    continue
                
                time_error_flag = 0
                for indx in indexDatetime:
                    myString[indx] = convertTime(myString[indx],dictDatetimeColumns[indexDatetime[indx]])
                    if myString[indx] == -1:
                        logger.debug("Error Data not in well timeformat-%s %s",str(myString[indx]),str(dictDatetimeColumns[indexDatetime[indx]]))
                        time_error_flag = 1
                        break
                if time_error_flag == 1:
                    continue
                myString = ["\'" + col.replace("'","''") + "\'" for col in myString]
                myString.append("'current'")
                myString.append(str(rept_hist_id))
                columnValue = ",".join(myString)
                logger.debug("%s",str(columnValue))
                insertQuery = "INSERT INTO " + transName + "_" + reportName + "(" + headers + ") values(" + columnValue + ")"
                logger.debug("insertdata-%s",str(insertQuery))
                cur.execute(insertQuery)
                lineCnt += 1
                #if (lineCnt % 100000) == 0:
                #    conn.commit()
            ######################
            
            #INSERT INTO HISTORY TABLE AND GET HISTORY ID
            logger.debug("trans_id-%s,reportName-%s",str(trans_id),str(reportName)) 
            
            #insertquery = "INSERT INTO app_reporthistory(id,report_id,start_time,stop_time,execution_time,file_name) VALUES (%s,%s, %s, %s, %s, '%s');"%(str(rept_hist_id),str(report_id),StartTime,EndTime,execute_time,rpt_file_name)
            logger.debug("insertquery-%s",str(insertquery))
            #cur.execute(insertquery)
            
            conn.commit()
            logger.debug("Data Inserted Successfully")
            response_data["Status"]= "Success"
            response_data["data"]= "Data Inserted Successfully"
        else:
            response_data["Status"]= "ERROR"
            response_data["data"]="File Not Present"
            logger.debug("File is Not Present")
        
        
    except Exception,ex:
        logger.error("Exception In Inserting Report Data Into Postgres Database %s",ex)
        response_data["Status"]= "ERROR"
        response_data["data"]= "Error in inserting Data into Databse"
    finally:
        if conn != None:
            pg_pool.putconn(conn)
        if conn1 != None:
            pg_pool.putconn(conn1)
    return 

@csrf_exempt
@login_required
def Update_Chart_Heading(request):
    conn = None
    
    report_name = request.POST.get('rptname')
    report_name = report_name.lower()
    chart_type = request.POST.get('chart_type')
    trans_name = request.POST.get('trans_name').lower() 
    newHeading = request.POST.get('newHeading')	

    try:
        conn = pg_pool.getconn()
        cur = conn.cursor()
        workspace_id=getWorkspaceId(cur,trans_name,)
        report_id=getReportId(cur,workspace_id,report_name)
        cur.execute("SELECT id FROM app_chart_type WHERE chart_name=%(chart)s;", {'chart':chart_type} )
        chart_id=cur.fetchone()[0]
        temp_dict={'newHeading':newHeading,'report':report_id, 'chart':chart_id}
        cur.execute("Update public.app_report_chart_config set chart_heading=%(newHeading)s where report_id=%(report)s and chart_id=%(chart)s;",temp_dict)
        conn.commit()
        response_data={'Status':'SUCCESS'}
    except Exception,ex:
        logger.error("UpdateReportChart Error!\n ->%s",ex)
        conn.rollback()
        response_data={'Status':'Error'}
        
    finally:
        if conn != None:
            pg_pool.putconn(conn)
    return HttpResponse(json.dumps(response_data), content_type="application/json")
# <<<<< ADD TRANSFORMER and REPORT to POSTGRESQL DATABASE -- ENDED <<<<<
