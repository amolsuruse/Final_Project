var userID="";
var isAdmin = "";
var isStaff = "";
var isActive = "";
var workspace_list = "";
var workspace_active_item = "";
var trans_wizard_curr_state = '';
var active_page = "";
var active_tab = "";
var table_coll=['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC','WIN','SPR','SUM','AUT','ANN']
//var table_coll1=['YEAR','JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC','WIN','SPR','SUM','AUT','ANN']


$(function ()
{
	active_page = window.location.href.split("/")[3];
	//active_tab = window.location.href.split("/")[4].replace("#","");    
		var dataForAPI={"userID":userID};
		jQuery.ajax({
			url:'getTransformerList',
			type:'POST',
			data:dataForAPI,
			timeout:0,//in milliseconds, default is 0 or no timeout
			dataType: 'json',//expected response type
			success: function(result){
				$(".workspace_list").find('option').remove().end();
				$("#rsnl").find('option').remove().end();
				$(".reportsummaryname_list").find('option').remove().end();
				console.log(result);
				if(result['Status']=="SUCCESS")
				{
					all_data = result['data'];
					workspace_list=all_data["region"]
					temp_type=all_data["temp_type"]
					for(var i = 0; i < workspace_list.length; i++)
					{
						
						var workspace = workspace_list[i];
						if(workspace_active_item == null)
						{
							workspace_active_item = workspace;
						}
						if(workspace_active_item == workspace)
						{
							workspace_active_item = workspace;
							var opt_str = "<option value=\"" + workspace + "\" selected>" +  workspace + "</option>";
						}
						else
						{
							var opt_str = "<option value=\"" + workspace + "\">" +  workspace + "</option>";
						}

						$(".workspace_list").append(opt_str);
					}
					temp_active_item="null"
					for(var i = 0; i < temp_type.length; i++)
					{
						
						var t_type = temp_type[i];
						//alert(t_type)
						//var workspace_id_name = workspace['name'] + "_" + workspace['id'];

						if(temp_active_item == "null")
						{
						
							temp_active_item = t_type;
						}
						
						if(temp_active_item == t_type)
						{
						
							var opt_str = "<option value=\"" + t_type + "\" selected>" +  t_type + "</option>";
						}
						else
						{
							var opt_str = "<option value=\"" + t_type + "\">" +  t_type + "</option>";
						}
						
						$(".reportsummaryname_list").append(opt_str);
						
					}
					
					for(var i = 0; i < table_coll.length; i++)
					{	
						if(i==0)
						{
							var start_op="select option"
						var opt_str = "<option value=\""+start_op+"\" selected>" +  start_op + "</option>";
						$('#coll_pie').append(opt_str);	
						$('#coll_bar').append(opt_str);	
						$('#coll_line').append(opt_str);	
						var opt_str = "<option value=\"" + table_coll[i] + "\">" +  table_coll[i] + "</option>";
						$('#coll_pie').append(opt_str);	
						$('#coll_bar').append(opt_str);	
						$('#coll_line').append(opt_str);	
						}
						else{
						var opt_str = "<option value=\"" + table_coll[i] + "\">" +  table_coll[i] + "</option>";
						$('#coll_pie').append(opt_str);	
						$('#coll_bar').append(opt_str);	
						$('#coll_line').append(opt_str);	
						}
					}						
					getReportSummaryChartsnGraphsData1()
				}
				else
				{
					alert("Error: " + result['Msg']);
				}				
		},
		error:function(x,e){
			alert("Protocol Error in getTransformerList");
		}
	});


function getReportSummaryChartsnGraphsData1()
{
	var reportName = $("#rsnl").val();
	if(reportName == null || reportName == "")
	{
		var transName = $('#sel').val();
		alert("No report(s) defined for workspace: " + transName);
		resetAllCharts();
		return;
	}
	var transName = $('#sel').val();
	var dataForAPI={"reportName":reportName,'transName': transName,'recordsPerPage':10, 'pageValue': 1,'type':'all','measure':"all"};
	if(dataForAPI['reportName'] == "" || dataForAPI['reportName'] == null)
	{
		resetAllCharts();
		return;
	}
	$.blockUI();
		$.ajax({
		url:'getReportChartData',
		type:'POST',
		data:dataForAPI,
		timeout:0,
		dataType: 'json',
		success: function(result)
		{		
			$.unblockUI();
			if(result['Status'] == 'ERROR')
			{
				resetAllCharts();
				alert(result['data']);
				return;
			}

			//set the data for PIE chart 
			var result_data = result['data'];
			var pie_chart_data = result_data['pie'];
			loadReportSummaryPieChartData(pie_chart_data);

			var bar_chart_data = result_data['bar'];
			loadReportSummaryBarChartData(bar_chart_data);

			var line_chart_data = result_data['line'];
			loadReportSummaryLineChartData(line_chart_data);

			var table_data = result_data['table'];
			loadReportSummaryTableData(table_data,1);
		},
		error:function(x,e)
		{
			 jQuery.unblockUI();
			 alert("Error in obtaining data for the report. Please check report configuration!");
		}
	});
}


	$('.modal ').on('show.bs.modal', function (e) {
	  $('input.form-control').removeClass('error');
	  $('label.error').css('display','none');
	})
});


$('#coll_pie').on('change',function(){
	var parameter=$('#coll_pie').val()
	var reportName = $("#rsnl").val();
	var transName = $('#sel').val();
	var dataForAPI={"reportName":reportName,'transName': transName,'recordsPerPage':10, 'pageValue': 1,'type':'pie','measure':parameter};
	$.blockUI();
	$.ajax({
		url:'getReportChartData',
		type:'POST',
		data:dataForAPI,
		timeout:0,
		dataType: 'json',
		success: function(result)
		{
			$.unblockUI();
			if(result['Status'] == 'ERROR')
			{
				resetAllCharts();
				alert(result['data']);
				return;
			}
			var result_data = result['data'];
			var pie_chart_data = result_data['pie'];
			loadReportSummaryPieChartData(pie_chart_data);
		},
		error:function(x,e)
		{
			 jQuery.unblockUI();
			 alert("Error in obtaining data for the report. Please check report configuration!");
		}
	});
})


$('#coll_bar').on('change',function(){
	var parameter=$('#coll_bar').val()
	
	var reportName = $("#rsnl").val();
	var transName = $('#sel').val();
	var dataForAPI={"reportName":reportName,'transName': transName,'recordsPerPage':10, 'pageValue': 1,'type':'bar','measure':parameter};
	$.blockUI();
	$.ajax({
		url:'getReportChartData',
		type:'POST',
		data:dataForAPI,
		timeout:0,
		dataType: 'json',
		success: function(result)
		{
			$.unblockUI();
			if(result['Status'] == 'ERROR')
			{
				resetAllCharts();
				alert(result['data']);
				return;
			}

			//set the data for PIE chart 
			var result_data = result['data'];
			var bar_chart_data = result_data['bar'];
			loadReportSummaryBarChartData(bar_chart_data);
		},
		error:function(x,e)
		{
			 jQuery.unblockUI();
			 alert("Error in obtaining data for the report. Please check report configuration!");
		}
	});
})



$('#coll_line').on('change',function(){
	var parameter=$('#coll_line').val()
	
	var reportName = $("#rsnl").val();
	var transName = $('#sel').val();
	
	
	var dataForAPI={"reportName":reportName,'transName': transName,'recordsPerPage':10, 'pageValue': 1,'type':'line','measure':parameter};
	$.blockUI();
	$.ajax({
		url:'getReportChartData',
		type:'POST',
		data:dataForAPI,
		timeout:0,
		dataType: 'json',
		success: function(result)
		{
			
			$.unblockUI();
			if(result['Status'] == 'ERROR')
			{
				resetAllCharts();
				alert(result['data']);
				return;
			}

			//set the data for PIE chart 
			var result_data = result['data'];
			var line_chart_data = result_data['line'];
			loadReportSummaryLineChartData(line_chart_data);

		},
		error:function(x,e)
		{
			 jQuery.unblockUI();
			 alert("Error in obtaining data for the report. Please check report configuration!");
		}
	});
})


$('#sel').on('change', function () { //UPDATED COMMON WORKSPACE SELECTION	
	var reportName = $("#rsnl").val();
	var transName = $('#sel').val();
	$('#coll_pie').val("JAN");
	$('#coll_bar').val("JAN");
	$('#coll_line').val("JAN");
	
	var dataForAPI={"reportName":reportName,'transName': transName,'recordsPerPage':10, 'pageValue': 1,'type':'all','measure':'all'};
	$.blockUI();
	$.ajax({
		url:'getReportChartData',
		type:'POST',
		data:dataForAPI,
		timeout:0,
		dataType: 'json',
		success: function(result)
		{

			$.unblockUI();
			if(result['Status'] == 'ERROR')
			{
				resetAllCharts();
				alert(result['data']);
				return;
			}

			//set the data for PIE chart 
			var result_data = result['data'];
			var pie_chart_data = result_data['pie'];
			loadReportSummaryPieChartData(pie_chart_data);
			loadReportSummaryPieChartData(pie_chart_data);

			//set the data for BAR chart
			//	bar_chart_data=pie_chart_data
			var bar_chart_data = result_data['bar'];
			loadReportSummaryBarChartData(bar_chart_data);

			//set the data for LINE chart 
			//line_chart_data=bar_chart_data
			var line_chart_data = result_data['line'];
			loadReportSummaryLineChartData(line_chart_data);

			var table_data = result_data['table'];
			loadReportSummaryTableData(table_data, dataForAPI, 1);


		},
		error:function(x,e)
		{
			 jQuery.unblockUI();
			 alert("Error in obtaining data for the report. Please check report configuration!");
		}
	});

});







function reportSummary_PieChart(PieData,fieldName)
{
  // Hover solution to refresh chart data
  $("#pieCanvas").html('&nbsp;');
  $("#pieCanvas").html('<canvas id="pieChart" height="120"></canvas>');

  // Get context with jQuery - using jQuery's .get() method.
  var pieChartCanvas = $("#pieChart").get(0).getContext("2d");

  var pieOptions = {
    scaleFontSize: 5,
    //Boolean - Whether we should show a stroke on each segment
    segmentShowStroke: true,
    //String - The colour of each segment stroke
    segmentStrokeColor: "#fff",
    //Number - The width of each segment stroke
    //Number - The width of each segment stroke
    segmentStrokeWidth: 1,
    //Number - The percentage of the chart that we cut out of the middle
    percentageInnerCutout: 0, // This is 50 for Doughnut charts
    //Number - Amount of animation steps
    animationSteps: 100,
    //String - Animation easing effect
    animationEasing: "easeOutBounce",
    //Boolean - Whether we animate the rotation of the Doughnut
    animateRotate: true,
    //Boolean - Whether we animate scaling the Doughnut from the centre
    animateScale: false,
    //Boolean - whether to make the chart responsive to window resizing
    responsive: true,
    // Boolean - whether to maintain the starting aspect ratio or not when responsive, if set to false, will take up entire container
    maintainAspectRatio: false,
    //String - A legend template
    legendTemplate: "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<segments.length; i++){%><li><span style=\"background-color:<%=segments[i].fillColor%>\"></span><%if(segments[i].label){%><%=segments[i].label%><%}%></li><%}%></ul>",
    //String - A tooltip template
    tooltipTemplate: "<%=value %> <%=label%>"
  };
  //Create pie or douhnut chart
  // You can switch between pie and douhnut using the method below.
  var pieChart = new Chart(pieChartCanvas).Pie(PieData, pieOptions);
  
	// Get data from chart on click
	$("#pieChart").on('click',function(evt){
            var activePoints = pieChart.getSegmentsAtEvent(evt);
            addFieldValueSelectionsHTMLStr(fieldName,activePoints[0]["label"])
    });
		
	// Change the cursor on hover
	var originalShowTooltip = pieChart.showTooltip;
	pieChart.showTooltip = function (activeElements) {
		$("#pieChart").css("cursor", activeElements.length ? "pointer" : "default");
		originalShowTooltip.apply(this, arguments);
	}
 
}

function reportSummary_BarChart(barChartData,fieldName)
{
  // Hover solution to refresh chart data
  $("#barCanvas").html('&nbsp;');
  $("#barCanvas").html('<canvas id="barChart" height="120"></canvas>');

  // Get context with jQuery - using jQuery's .get() method.
  var barChartCanvas = $("#barChart").get(0).getContext("2d");

  var barChartOptions = {
    scaleFontSize: 10,
    labelLength: 10,
    //Boolean - If we should show the scale at all
    showScale: true,
    //Boolean - Whether grid lines are shown across the chart
    scaleShowGridLines: false,
    //String - Colour of the grid lines
    scaleGridLineColor: "rgba(0,0,0,.05)",
    //Number - Width of the grid lines
    scaleGridLineWidth: 1,
    //Boolean - Whether to show horizontal lines (except X axis)
    scaleShowHorizontalLines: true,
    //Boolean - Whether to show vertical lines (except Y axis)
    scaleShowVerticalLines: true,
    //Boolean - Whether the line is curved between points
    bezierCurve: true,
    //Number - Tension of the bezier curve between points
    bezierCurveTension: 0.3,
    //Boolean - Whether to show a dot for each point
    pointDot: false,
    //Number - Radius of each point dot in pixels
    pointDotRadius: 4,
    //Number - Pixel width of point dot stroke
    pointDotStrokeWidth: 1,
    //Number - amount extra to add to the radius to cater for hit detection outside the drawn point
    pointHitDetectionRadius: 20,
    //Boolean - Whether to show a stroke for datasets
    datasetStroke: true,
    //Number - Pixel width of dataset stroke
    datasetStrokeWidth: 2,
    //Boolean - Whether to fill the dataset with a color
    datasetFill: true,
    //String - A legend template
    legendTemplate: "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].lineColor%>\"></span><%=datasets[i].label%></li><%}%></ul>",
    //Boolean - whether to maintain the starting aspect ratio or not when responsive, if set to false, will take up entire container
    maintainAspectRatio: false,
    //Boolean - whether to make the chart responsive to window resizing
    responsive: true
  };

  if($.isEmptyObject(barChartData) == false)
	{
  //Create the line chart
  var barChart = new Chart(barChartCanvas).Bar(barChartData, barChartOptions);

  

  //---------------------------
  //- END  bar CHART -
  //---------------------------
  
	// Get data from chart on click
	$("#barChart").on('click',function(evt){
            var activePoints = barChart.getBarsAtEvent(evt);
            addFieldValueSelectionsHTMLStr(fieldName,activePoints[0]["label"])

    });
		
	// Change the cursor on hover
	var originalShowTooltip = barChart.showTooltip;
	barChart.showTooltip = function (activeElements) {
		$("#barChart").css("cursor", activeElements.length ? "pointer" : "default");
		originalShowTooltip.apply(this, arguments);
	}
	}
}

function reportSummary_ServerChart(serverChartData,fieldName)
{
  // Hover solution to refresh chart data
  $("#serverCanvas").html('&nbsp;');
  $("#serverCanvas").html('<canvas id="serverChart" height="120"></canvas>');

  // Get context with jQuery - using jQuery's .get() method.
  var serverChartCanvas = $("#serverChart").get(0).getContext("2d");

  var serverChartOptions = {
    scaleFontSize: 10,
    labelLength: 10,
    //Boolean - If we should show the scale at all
    showScale: true,
    //Boolean - Whether grid lines are shown across the chart
    scaleShowGridLines: false,
    //String - Colour of the grid lines
    scaleGridLineColor: "rgba(0,0,0,.05)",
    //Number - Width of the grid lines
    scaleGridLineWidth: 1,
    //Boolean - Whether to show horizontal lines (except X axis)
    scaleShowHorizontalLines: true,
    //Boolean - Whether to show vertical lines (except Y axis)
    scaleShowVerticalLines: true,
    //Boolean - Whether the line is curved between points
    bezierCurve: true,
    //Number - Tension of the bezier curve between points
    bezierCurveTension: 0.3,
    //Boolean - Whether to show a dot for each point
    pointDot: false,
    //Number - Radius of each point dot in pixels
    pointDotRadius: 4,
    //Number - Pixel width of point dot stroke
    pointDotStrokeWidth: 1,
    //Number - amount extra to add to the radius to cater for hit detection outside the drawn point
    pointHitDetectionRadius: 20,
    //Boolean - Whether to show a stroke for datasets
    datasetStroke: true,
    //Number - Pixel width of dataset stroke
    datasetStrokeWidth: 2,
    //Boolean - Whether to fill the dataset with a color
    datasetFill: true,
    //String - A legend template
    legendTemplate: "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].lineColor%>\"></span><%=datasets[i].label%></li><%}%></ul>",
    //Boolean - whether to maintain the starting aspect ratio or not when responsive, if set to false, will take up entire container
    maintainAspectRatio: false,
    //Boolean - whether to make the chart responsive to window resizing
    responsive: true
  };

  if($.isEmptyObject(serverChartData) == false)
	{
  //Create the line chart
  var serverChart = new Chart(serverChartCanvas).Line(serverChartData, serverChartOptions);

	var originalShowTooltip = serverChart.showTooltip;
	serverChart.showTooltip = function (activeElements) {
		$("#serverChart").css("cursor", activeElements.length ? "pointer" : "default");
		originalShowTooltip.apply(this, arguments);
	}
	}
}

$('#rsnl').on('change', function () { //UPDATED REPORT SUMMARY REPORT SELECTION

	var reportName = $("#rsnl").val();
	var transName = $('#sel').val();
	$('#coll_pie').val("JAN");
	$('#coll_bar').val("JAN");
	$('#coll_line').val("JAN");
	
	var dataForAPI={"reportName":reportName,'transName': transName,'recordsPerPage':10, 'pageValue': 1,'type':'all','measure':'all'};
	$.blockUI();
	$.ajax({
		url:'getReportChartData',
		type:'POST',
		data:dataForAPI,
		timeout:0,
		dataType: 'json',
		success: function(result)
		{
			$.unblockUI();
			if(result['Status'] == 'ERROR')
			{
				resetAllCharts();
				alert(result['data']);
				return;
			}
			//set the data for PIE chart 
			var result_data = result['data'];
			var pie_chart_data = result_data['pie'];
			loadReportSummaryPieChartData(pie_chart_data);

			var bar_chart_data = result_data['bar'];
			loadReportSummaryBarChartData(bar_chart_data);

			var line_chart_data = result_data['line'];
			loadReportSummaryLineChartData(line_chart_data);

			var table_data = result_data['table'];
			loadReportSummaryTableData(table_data, dataForAPI, 1);
		},
		error:function(x,e)
		{
			 jQuery.unblockUI();
			 alert("Error in obtaining data for the report. Please check report configuration!");
		}
	});
});

$('#submitselections').on('click', function(){	

jQuery.blockUI();
dataForAPI={}
$.ajax({
		url:'load_dat_from_web',
		type:'POST',
		data:dataForAPI,
		timeout:0,
		dataType: 'json',
		success: function(result)
		{
			jQuery.unblockUI();
			alert(result["msg"])
			$( "#clearselections" ).click();

		},
		error:function(x,e)
		{
			 jQuery.unblockUI();
			 alert("Error in obtaining data for the report. Please check report configuration!");
		}
	});
});

	
$('button#clearselections').on('click', function() {
	
	
	jQuery.blockUI();
	var reportName = $("#rsnl").val();
	var transName = $('#sel').val();
	$('#coll_pie').val("JAN");
	$('#coll_bar').val("JAN");
	$('#coll_line').val("JAN");
	
	var dataForAPI={"reportName":reportName,'transName': transName,'recordsPerPage':10, 'pageValue': 1,'type':'all','measure':'all'};
	
	$.ajax({
		url:'getReportChartData',
		type:'POST',
		data:dataForAPI,
		timeout:0,
		dataType: 'json',
		success: function(result)
		{
			
			$.unblockUI();
			if(result['Status'] == 'ERROR')
			{
				resetAllCharts();
				alert(result['data']);
				return;
			}

			//set the data for PIE chart 
			var result_data = result['data'];
			var pie_chart_data = result_data['pie'];
			loadReportSummaryPieChartData(pie_chart_data);

			//set the data for BAR chart
			//	bar_chart_data=pie_chart_data
			var bar_chart_data = result_data['bar'];
			loadReportSummaryBarChartData(bar_chart_data);

			//set the data for LINE chart 
			//line_chart_data=bar_chart_data
			var line_chart_data = result_data['line'];
			loadReportSummaryLineChartData(line_chart_data);

			var table_data = result_data['table'];
			loadReportSummaryTableData(table_data, dataForAPI, 1);


		},
		error:function(x,e)
		{
			 jQuery.unblockUI();
			 alert("Error in obtaining data for the report. Please check report configuration!");
		}
	});
});

function reportSummary_formatPieData(data)
{
	var pie_data = [];
	
	var i = 0;
	for (var row in data)
	{
		
		pie_data.push({	value: data[row]['value'],
						color: getHexColor(i),
						highlight: getHexColor(i),
						label: data[row]['key']
					  });
		i = i+1;
	}
	
	return pie_data;
}

function reportSummary_formatBarData(data)
{
	var x_axis = []
	var y_axis = []
	
	for (var i = 0; i < data['Data'].length; i++)
	{
		x_axis.push(data['Data'][i]['key']);
		y_axis.push(data['Data'][i]['value']);
	}
	
	var barChartData = {
	labels: x_axis,
    datasets: [
      {
	    label: data['Config'][3],
        fillColor: "rgba(60,141,188,0.9)",
        strokeColor: "rgba(60,141,188,0.8)",
        pointColor: "#3b8bba",
        pointStrokeColor: "rgba(60,141,188,1)",
        pointHighlightFill: "#fff",
        pointHighlightStroke: "rgba(60,141,188,1)",
		data: y_axis
      }
    ]
  };
	console.log(barChartData)
	
	return barChartData;
}

function reportSummary_formatServerChartData(data)
{
	var x_axis = []
	var y_axis = []
	
	for (var i = 0; i < data['Data'].length; i++)
	{
		x_axis.push(data['Data'][i]['key']);
		y_axis.push(data['Data'][i]['value']);
	}
	
	var serverChartData = {
	labels: x_axis,
    datasets: [
      {
	    label: data['Config'][3],
        fillColor: "rgba(60,141,188,0.9)",
        strokeColor: "rgba(60,141,188,0.8)",
        pointColor: "#3b8bba",
        pointStrokeColor: "rgba(60,141,188,1)",
        pointHighlightFill: "#fff",
        pointHighlightStroke: "rgba(60,141,188,1)",
		data: y_axis
      }
    ]
  };
  
  console.log(serverChartData)
	
  return serverChartData;
}


function getCharts()
{
	
	var reportName = $("#rsnl").val();

	if(reportName == null || reportName == "")
	{
		var transName = $('#sel').val();
		alert("No report(s) defined for workspace: " + transName);
		resetAllCharts();
		return;
	}
var transName = $('#sel').val();

	var dataForAPI={"reportName":reportName,'transName': transName,'recordsPerPage':10, 'pageValue': 1};

}


function getReportSummaryTable(dataForAPI, newPageValue)
{
	dataForAPI['pagination_request'] = 'true';
	$.blockUI();
        $.ajax({
                url:'getReportChartData',
                type:'POST',
                data:dataForAPI,
                timeout:0,
                dataType: 'json',
                success: function(result)
                {
                        $.unblockUI();
                        if(result['Status'] == 'ERROR')
                        {
                                resetAllCharts();
                                alert(result['data']);
                                return;
                        }

                        var table_data = result['table'];
                        loadReportSummaryTableData(table_data, dataForAPI, newPageValue);
                },
                error:function(x,e)
                {
                     jQuery.unblockUI();
                     alert("Error in obtaining Table data for the report.");
                }
        });
}

function resetAllCharts()
{
	reportSummary_PieChart([],"");
	$("#pieChartHead").html("No Data / Config Not Defined To Show Pie Chart");
	reportSummary_BarChart({},"");
	$("#barChartHead").html("No Data / Config Not Defined To Show Bar Chart");
	reportSummary_ServerChart({},"");
	$("#serverChartHead").html("No Data / Config Not Defined To Show Line Chart");
	$('#reportsummarytype').bootstrapTable("destroy");
	$("#rsummary_pager").html("<div style='padding-left:45px';>No Data / Config Not Defined To Show Table</div>");
}

function loadReportSummaryPieChartData(result)
{
	
	result['Config']['chart_heading'] = ""
	if(result['Status'] == "Success" || result['Data'].length != 0)
	{
		reportSummary_PieChart(reportSummary_formatPieData(result['Data']),result['Config']['field_1']);

		if(result['Config']['chart_heading'] == "" || result['Config']['chart_heading'] == null)
		{
			$("#pieChartHead").html(result['Config']['field_1'] + " wise summary");
		}
		else
		{
			$("#pieChartHead").html(result['Config']['chart_heading'].toLowerCase());
		}
	}
	else
	{
		reportSummary_PieChart([],"");
		$("#pieChartHead").html("No Data / Config Not Defined To Show Pie Chart");
	}
}


function loadReportSummaryBarChartData(result)
{
	result['Config']['chart_heading'] = ""
	if(result['Status'] == "Success" && result['Data'].length != 0)
	{
		reportSummary_BarChart(reportSummary_formatBarData(result),result['Config']['field_1']);

		if(result['Config']['chart_heading'] == "" || result['Config']['chart_heading'] == null)
		{
		
			$("#barChartHead").html(result['Config']['field_1'] + " wise summary");
		}
		else
		{
			$("#barChartHead").html(result['Config']['chart_heading'].toLowerCase());
		}
	}
	else
	{
		reportSummary_BarChart({},"");
		$("#barChartHead").html("No Data / Config Not Defined To Show Bar Chart");
	}
}

function loadReportSummaryLineChartData(result)
{
	result['Config']['chart_heading'] = ""
	if(result['Status'] == "Success" && result['Data'].length != 0)
	{
		reportSummary_ServerChart(reportSummary_formatServerChartData(result),result['Config']['field_1']);
		if(result['Config']['chart_heading'] =="")
		{
			
			$("#serverChartHead").html(result['Config']['field_1']+" wise summary");
		}
		else
		{
			alert("in else")
			var line_header = result['Config']['field_1'].substring(result['Config']['field_1'].indexOf("(") + 1,result['Config']['field_1'].indexOf(" "));
			line_header = line_header.replace(/\"/g, '') + " trend";
			if(result['Config']['chart_heading'] != null && result['Config']['chart_heading'] != "")
			{
				$("#serverChartHead").html(result['Config']['chart_heading'].toLowerCase());
			}
			else
			{
				$("#serverChartHead").html(line_header.toLowerCase());
			}
		}
	}
	else
	{
		reportSummary_ServerChart({},"");
		$("#serverChartHead").html("No Data / Config Not Defined To Show Line Chart");
	}
}


function escapeXml (s) {
	var XML_CHAR_MAP = {
	  '<': '&lt;',
	  '>': '&gt;',
	  '&': '&amp;',
	  '"': '&quot;',
	  "'": '&apos;'
	}

	if(typeof(s) == 'string')
	{
 		return s.replace(/[<>&"']/g, function (ch) {
    	return XML_CHAR_MAP[ch]
  	})
	}
	else
	{
		return s;
	}
}

function loadReportSummaryTableData(result,pageValue)
{
	
	//alert("loadReportSummaryTableData")
	dataForAPI={"recordsPerPage":1000}
	//result["Data_Count"][0]["count"]=100
	

	//alert("from loadReportSummaryTableData-592")
	var table = $('#reportsummarytype');
	table.bootstrapTable("destroy");

	if(result.Status == "Success")
	{
		
		var reportHeaders = [];
		console.log(result);

		if(result["Data"].length != 0)
		{

			var dateColumn = 'omsai';
			console.log("dateColumn: " + dateColumn);

			var rows = []
			
			for(var i = 0; i < result["Data"].length; i++)
			{
				if(i == 0)
				{
					var first_row = {}
					for(var key in result["Data"][i])
					{
						
						reportHeaders.push({
							field: key,
							title: key,
							searchable: true,
							sortable: true
						});

						first_row[key]=escapeXml(result["Data"][i][key]);
					}

					table.bootstrapTable({
						advancedSearch: false,
						flat: false,
						onSearch: function (text) {
							$(".box").activateBox();
						},
						columns:reportHeaders,
						pagination:false,
					});

					rows.push(first_row);
				}
				else
				{
					var row = {}
					for(var key in result["Data"][i])
					{
						row[key]=escapeXml(result["Data"][i][key]);
					}
					rows.push(row);
				}
			}

			var $search = table.data('bootstrap.table').$toolbar.find('.bars');

			if($("#advancedReportSearch").length > 0)
			{
				$("#advancedReportSearch").remove();
			}

			$search.append('<button class="btn btn-default" type="button" id="advancedReportSearch" name="advancedReportSearch" title="Advanced Search"><i class="fa fa-search icon-search"></i></button>');

			table.bootstrapTable('load', rows);
			$(".box").activateBox();

			$('#advancedReportSearch').on('click',function()
			{
				if($(".txtAFCol")[0])
				{
					$(".txtAFCol").remove();
				}
				else
				{
					console.log("Date Column: " + dateColumn);
					for(var item in first_row)
					{
						var $data_field = table.find('thead > tr > th')
						for (var i = 0; i < $data_field.length; i++)
						{
							if($data_field[i].textContent != dateColumn)
							{
								$data_field[i].children[1].innerHTML ='<input class="txtAFCol" type="text" name="'+ $data_field[i].textContent + '">';
							}
						}
					}
					$(".txtAFCol").keyup(function (e) {
						if (e.which == 13) {
							getCharts();
						}
					 });
				}
			});
		}
		else
		{
			jQuery("#rsummary_pager").html("<div style='padding-left:45px';>No Data / Config Not Defined To Show Table</div>");
			return {};
		}
	}
	else
	{
		jQuery("#rsummary_pager").html("<div style='padding-left:45px';>No Data / Config Not Defined To Show Table</div>");
		if(result['Data'].length != 0)
		{
			alert(result['Data']);
		}
		return {};
	}
}



function addFieldValueSelectionsHTMLStr(fieldName,value)  // NEW
{
	var SelectStr = "<span>"+fieldName+" = '"+value+"'</span>";
	SelectStr += "<a><i class='remove glyphicon glyphicon-remove-sign glyphicon-white'></i></a>";
	
	var newText = fieldName+" = '"+value+"'";
	var flag = 0;
	var children = document.getElementById("selections").children;
	for (var i = 0; i < children.length; i++) {
		var innerSpanChildText = children[i].children[0].innerText;
		if (innerSpanChildText == newText)
		{
		  flag = 1;
		  //alert("Already Selected. Select Other Values !!!");
		  removeFieldValueSelectionHTMLStr(fieldName,value);
		  return false;
		}
	}
	
	if(flag == 0)
	{
		var div = document.getElementById("selections");
		var span = document.createElement("span");
		span.className= 'tag label label-success';
		span.innerHTML = SelectStr;
		span.onclick = function() {
			//this.parentNode.removeChild(this);
			removeFieldValueSelectionHTMLStr(fieldName,value);
			if(div.childElementCount == 0){$("#selections").slideUp('slow'); }
			}
		if(div.childElementCount == 10)
		{ alert("Selections Limit Reached (Max. 10). Remove Some Selections.");}
		/*else if (div.childElementCount == 0)
		{ div.appendChild(span);}*/
		else
		{
			//div.insertBefore(span, div.firstChild);
			$("#selections").slideDown('slow');
			div.appendChild(span);
		}
	}
}

function removeFieldValueSelectionHTMLStr(fieldName,value) // NEW
{
	var unSelectedText = fieldName+" = '"+value+"'";
	var subspan = $("#selections > span > span").filter(function() { return ($(this).text().indexOf(fieldName+" = '"+value+"'") > -1) });
	(subspan[0].parentNode).parentNode.removeChild(subspan[0].parentNode);
	if(document.getElementById("selections").childElementCount == 0){$("#selections").slideUp('slow');}
}





















/*var dashboard_context = {
	no_of_events:10,
	is_autorefresh_enabled:0,
	autorefresh_dashboard:null,
	autorefresh_interval:15,
	evrate_timeout_retvalue:null,
	db_timeout_retvalue:null,
	metric_timeout_retvalue:null,
	current_context:null,
	metadata_list:{},
	selected_metric_list:[],
	metric_db_handle:null, 
	graph1:null,
	graph2:null,
	pie1:null,
	alertHandle:null,
	scriptDashboardTableObj:null,
	dbTableObj:null,
	metricTableObj:null,
};*/


var random_colors_list = [
    {
        "hex": "#f56954", 
        "name": "Mat Red", 
        "rgb": "(245,105,84)"
    },
	{
        "hex": "#00a65a", 
        "name": "Mat Green", 
        "rgb": "(0,166,90)"
    },
	{
        "hex": "#f39c12", 
        "name": "Mat Orange", 
        "rgb": "(243,156,18)"
    },
	{
        "hex": "#00c0ef", 
        "name": "Mat Blue", 
        "rgb": "(0,192,239)"
    },
	{
        "hex": "#3c8dbc", 
        "name": "Mat Sky Blue", 
        "rgb": "(60,141,188)"
    },
	{
        "hex": "#d2d6de", 
        "name": "Mat Grey", 
        "rgb": "(210,214,222)"
    },
    {
        "hex": "#EFDECD", 
        "name": "Almond", 
        "rgb": "(239, 222, 205)"
    }, 
    {
        "hex": "#CD9575", 
        "name": "Antique Brass", 
        "rgb": "(205, 149, 117)"
    }, 
    {
        "hex": "#FDD9B5", 
        "name": "Apricot", 
        "rgb": "(253, 217, 181)"
    }, 
    {
        "hex": "#78DBE2", 
        "name": "Aquamarine", 
        "rgb": "(120, 219, 226)"
    }, 
    {
        "hex": "#87A96B", 
        "name": "Asparagus", 
        "rgb": "(135, 169, 107)"
    }, 
    {
        "hex": "#FFA474", 
        "name": "Atomic Tangerine", 
        "rgb": "(255, 164, 116)"
    }, 
    {
        "hex": "#FAE7B5", 
        "name": "Banana Mania", 
        "rgb": "(250, 231, 181)"
    }, 
    {
        "hex": "#9F8170", 
        "name": "Beaver", 
        "rgb": "(159, 129, 112)"
    }, 
    {
        "hex": "#FD7C6E", 
        "name": "Bittersweet", 
        "rgb": "(253, 124, 110)"
    }, 
    {
        "hex": "#000000", 
        "name": "Black", 
        "rgb": "(0,0,0)"
    }, 
    {
        "hex": "#ACE5EE", 
        "name": "Blizzard Blue", 
        "rgb": "(172, 229, 238)"
    }, 
    {
        "hex": "#1F75FE", 
        "name": "Blue", 
        "rgb": "(31, 117, 254)"
    }, 
    {
        "hex": "#A2A2D0", 
        "name": "Blue Bell", 
        "rgb": "(162, 162, 208)"
    }, 
    {
        "hex": "#6699CC", 
        "name": "Blue Gray", 
        "rgb": "(102, 153, 204)"
    }, 
    {
        "hex": "#0D98BA", 
        "name": "Blue Green", 
        "rgb": "(13, 152, 186)"
    }, 
    {
        "hex": "#7366BD", 
        "name": "Blue Violet", 
        "rgb": "(115, 102, 189)"
    }, 
    {
        "hex": "#DE5D83", 
        "name": "Blush", 
        "rgb": "(222, 93, 131)"
    }, 
    {
        "hex": "#CB4154", 
        "name": "Brick Red", 
        "rgb": "(203, 65, 84)"
    }, 
    {
        "hex": "#B4674D", 
        "name": "Brown", 
        "rgb": "(180, 103, 77)"
    }, 
    {
        "hex": "#FF7F49", 
        "name": "Burnt Orange", 
        "rgb": "(255, 127, 73)"
    }, 
    {
        "hex": "#EA7E5D", 
        "name": "Burnt Sienna", 
        "rgb": "(234, 126, 93)"
    }, 
    {
        "hex": "#B0B7C6", 
        "name": "Cadet Blue", 
        "rgb": "(176, 183, 198)"
    }, 
    {
        "hex": "#FFFF99", 
        "name": "Canary", 
        "rgb": "(255, 255, 153)"
    }, 
    {
        "hex": "#1CD3A2", 
        "name": "Caribbean Green", 
        "rgb": "(28, 211, 162)"
    }, 
    {
        "hex": "#FFAACC", 
        "name": "Carnation Pink", 
        "rgb": "(255, 170, 204)"
    }, 
    {
        "hex": "#DD4492", 
        "name": "Cerise", 
        "rgb": "(221, 68, 146)"
    }, 
    {
        "hex": "#1DACD6", 
        "name": "Cerulean", 
        "rgb": "(29, 172, 214)"
    }, 
    {
        "hex": "#BC5D58", 
        "name": "Chestnut", 
        "rgb": "(188, 93, 88)"
    }, 
    {
        "hex": "#DD9475", 
        "name": "Copper", 
        "rgb": "(221, 148, 117)"
    }, 
    {
        "hex": "#9ACEEB", 
        "name": "Cornflower", 
        "rgb": "(154, 206, 235)"
    }, 
    {
        "hex": "#FFBCD9", 
        "name": "Cotton Candy", 
        "rgb": "(255, 188, 217)"
    }, 
    {
        "hex": "#FDDB6D", 
        "name": "Dandelion", 
        "rgb": "(253, 219, 109)"
    }, 
    {
        "hex": "#2B6CC4", 
        "name": "Denim", 
        "rgb": "(43, 108, 196)"
    }, 
    {
        "hex": "#EFCDB8", 
        "name": "Desert Sand", 
        "rgb": "(239, 205, 184)"
    }, 
    {
        "hex": "#6E5160", 
        "name": "Eggplant", 
        "rgb": "(110, 81, 96)"
    }, 
    {
        "hex": "#CEFF1D", 
        "name": "Electric Lime", 
        "rgb": "(206, 255, 29)"
    }, 
    {
        "hex": "#71BC78", 
        "name": "Fern", 
        "rgb": "(113, 188, 120)"
    }, 
    {
        "hex": "#6DAE81", 
        "name": "Forest Green", 
        "rgb": "(109, 174, 129)"
    }, 
    {
        "hex": "#C364C5", 
        "name": "Fuchsia", 
        "rgb": "(195, 100, 197)"
    }, 
    {
        "hex": "#CC6666", 
        "name": "Fuzzy Wuzzy", 
        "rgb": "(204, 102, 102)"
    }, 
    {
        "hex": "#E7C697", 
        "name": "Gold", 
        "rgb": "(231, 198, 151)"
    }, 
    {
        "hex": "#FCD975", 
        "name": "Goldenrod", 
        "rgb": "(252, 217, 117)"
    }, 
    {
        "hex": "#A8E4A0", 
        "name": "Granny Smith Apple", 
        "rgb": "(168, 228, 160)"
    }, 
    {
        "hex": "#95918C", 
        "name": "Gray", 
        "rgb": "(149, 145, 140)"
    }, 
    {
        "hex": "#1CAC78", 
        "name": "Green", 
        "rgb": "(28, 172, 120)"
    }, 
    {
        "hex": "#1164B4", 
        "name": "Green Blue", 
        "rgb": "(17, 100, 180)"
    }, 
    {
        "hex": "#F0E891", 
        "name": "Green Yellow", 
        "rgb": "(240, 232, 145)"
    }, 
    {
        "hex": "#FF1DCE", 
        "name": "Hot Magenta", 
        "rgb": "(255, 29, 206)"
    }, 
    {
        "hex": "#B2EC5D", 
        "name": "Inchworm", 
        "rgb": "(178, 236, 93)"
    }, 
    {
        "hex": "#5D76CB", 
        "name": "Indigo", 
        "rgb": "(93, 118, 203)"
    }, 
    {
        "hex": "#CA3767", 
        "name": "Jazzberry Jam", 
        "rgb": "(202, 55, 103)"
    }, 
    {
        "hex": "#3BB08F", 
        "name": "Jungle Green", 
        "rgb": "(59, 176, 143)"
    }, 
    {
        "hex": "#FEFE22", 
        "name": "Laser Lemon", 
        "rgb": "(254, 254, 34)"
    }, 
    {
        "hex": "#FCB4D5", 
        "name": "Lavender", 
        "rgb": "(252, 180, 213)"
    }, 
    {
        "hex": "#FFF44F", 
        "name": "Lemon Yellow", 
        "rgb": "(255, 244, 79)"
    }, 
    {
        "hex": "#FFBD88", 
        "name": "Macaroni and Cheese", 
        "rgb": "(255, 189, 136)"
    }, 
    {
        "hex": "#F664AF", 
        "name": "Magenta", 
        "rgb": "(246, 100, 175)"
    }, 
    {
        "hex": "#AAF0D1", 
        "name": "Magic Mint", 
        "rgb": "(170, 240, 209)"
    }, 
    {
        "hex": "#CD4A4C", 
        "name": "Mahogany", 
        "rgb": "(205, 74, 76)"
    }, 
    {
        "hex": "#EDD19C", 
        "name": "Maize", 
        "rgb": "(237, 209, 156)"
    }, 
    {
        "hex": "#979AAA", 
        "name": "Manatee", 
        "rgb": "(151, 154, 170)"
    }, 
    {
        "hex": "#FF8243", 
        "name": "Mango Tango", 
        "rgb": "(255, 130, 67)"
    }, 
    {
        "hex": "#C8385A", 
        "name": "Maroon", 
        "rgb": "(200, 56, 90)"
    }, 
    {
        "hex": "#EF98AA", 
        "name": "Mauvelous", 
        "rgb": "(239, 152, 170)"
    }, 
    {
        "hex": "#FDBCB4", 
        "name": "Melon", 
        "rgb": "(253, 188, 180)"
    }, 
    {
        "hex": "#1A4876", 
        "name": "Midnight Blue", 
        "rgb": "(26, 72, 118)"
    }, 
    {
        "hex": "#30BA8F", 
        "name": "Mountain Meadow", 
        "rgb": "(48, 186, 143)"
    }, 
    {
        "hex": "#C54B8C", 
        "name": "Mulberry", 
        "rgb": "(197, 75, 140)"
    }, 
    {
        "hex": "#1974D2", 
        "name": "Navy Blue", 
        "rgb": "(25, 116, 210)"
    }, 
    {
        "hex": "#FFA343", 
        "name": "Neon Carrot", 
        "rgb": "(255, 163, 67)"
    }, 
    {
        "hex": "#BAB86C", 
        "name": "Olive Green", 
        "rgb": "(186, 184, 108)"
    }, 
    {
        "hex": "#FF7538", 
        "name": "Orange", 
        "rgb": "(255, 117, 56)"
    }, 
    {
        "hex": "#FF2B2B", 
        "name": "Orange Red", 
        "rgb": "(255, 43, 43)"
    }, 
    {
        "hex": "#F8D568", 
        "name": "Orange Yellow", 
        "rgb": "(248, 213, 104)"
    }, 
    {
        "hex": "#E6A8D7", 
        "name": "Orchid", 
        "rgb": "(230, 168, 215)"
    }, 
    {
        "hex": "#414A4C", 
        "name": "Outer Space", 
        "rgb": "(65, 74, 76)"
    }, 
    {
        "hex": "#FF6E4A", 
        "name": "Outrageous Orange", 
        "rgb": "(255, 110, 74)"
    }, 
    {
        "hex": "#1CA9C9", 
        "name": "Pacific Blue", 
        "rgb": "(28, 169, 201)"
    }, 
    {
        "hex": "#FFCFAB", 
        "name": "Peach", 
        "rgb": "(255, 207, 171)"
    }, 
    {
        "hex": "#C5D0E6", 
        "name": "Periwinkle", 
        "rgb": "(197, 208, 230)"
    }, 
    {
        "hex": "#FDDDE6", 
        "name": "Piggy Pink", 
        "rgb": "(253, 221, 230)"
    }, 
    {
        "hex": "#158078", 
        "name": "Pine Green", 
        "rgb": "(21, 128, 120)"
    }, 
    {
        "hex": "#FC74FD", 
        "name": "Pink Flamingo", 
        "rgb": "(252, 116, 253)"
    }, 
    {
        "hex": "#F78FA7", 
        "name": "Pink Sherbet", 
        "rgb": "(247, 143, 167)"
    }, 
    {
        "hex": "#8E4585", 
        "name": "Plum", 
        "rgb": "(142, 69, 133)"
    }, 
    {
        "hex": "#7442C8", 
        "name": "Purple Heart", 
        "rgb": "(116, 66, 200)"
    }, 
    {
        "hex": "#9D81BA", 
        "name": "Purple Mountain's Majesty", 
        "rgb": "(157, 129, 186)"
    }, 
    {
        "hex": "#FE4EDA", 
        "name": "Purple Pizzazz", 
        "rgb": "(254, 78, 218)"
    }, 
    {
        "hex": "#FF496C", 
        "name": "Radical Red", 
        "rgb": "(255, 73, 108)"
    }, 
    {
        "hex": "#D68A59", 
        "name": "Raw Sienna", 
        "rgb": "(214, 138, 89)"
    }, 
    {
        "hex": "#714B23", 
        "name": "Raw Umber", 
        "rgb": "(113, 75, 35)"
    }, 
    {
        "hex": "#FF48D0", 
        "name": "Razzle Dazzle Rose", 
        "rgb": "(255, 72, 208)"
    }, 
    {
        "hex": "#E3256B", 
        "name": "Razzmatazz", 
        "rgb": "(227, 37, 107)"
    }, 
    {
        "hex": "#EE204D", 
        "name": "Red", 
        "rgb": "(238,32 ,77 )"
    }, 
    {
        "hex": "#FF5349", 
        "name": "Red Orange", 
        "rgb": "(255, 83, 73)"
    }, 
    {
        "hex": "#C0448F", 
        "name": "Red Violet", 
        "rgb": "(192, 68, 143)"
    }, 
    {
        "hex": "#1FCECB", 
        "name": "Robin's Egg Blue", 
        "rgb": "(31, 206, 203)"
    }, 
    {
        "hex": "#7851A9", 
        "name": "Royal Purple", 
        "rgb": "(120, 81, 169)"
    }, 
    {
        "hex": "#FF9BAA", 
        "name": "Salmon", 
        "rgb": "(255, 155, 170)"
    }, 
    {
        "hex": "#FC2847", 
        "name": "Scarlet", 
        "rgb": "(252, 40, 71)"
    }, 
    {
        "hex": "#76FF7A", 
        "name": "Screamin' Green", 
        "rgb": "(118, 255, 122)"
    }, 
    {
        "hex": "#9FE2BF", 
        "name": "Sea Green", 
        "rgb": "(159, 226, 191)"
    }, 
    {
        "hex": "#A5694F", 
        "name": "Sepia", 
        "rgb": "(165, 105, 79)"
    }, 
    {
        "hex": "#8A795D", 
        "name": "Shadow", 
        "rgb": "(138, 121, 93)"
    }, 
    {
        "hex": "#45CEA2", 
        "name": "Shamrock", 
        "rgb": "(69, 206, 162)"
    }, 
    {
        "hex": "#FB7EFD", 
        "name": "Shocking Pink", 
        "rgb": "(251, 126, 253)"
    }, 
    {
        "hex": "#CDC5C2", 
        "name": "Silver", 
        "rgb": "(205, 197, 194)"
    }, 
    {
        "hex": "#80DAEB", 
        "name": "Sky Blue", 
        "rgb": "(128, 218, 235)"
    }, 
    {
        "hex": "#ECEABE", 
        "name": "Spring Green", 
        "rgb": "(236, 234, 190)"
    }, 
    {
        "hex": "#FFCF48", 
        "name": "Sunglow", 
        "rgb": "(255, 207, 72)"
    }, 
    {
        "hex": "#FD5E53", 
        "name": "Sunset Orange", 
        "rgb": "(253, 94, 83)"
    }, 
    {
        "hex": "#FAA76C", 
        "name": "Tan", 
        "rgb": "(250, 167, 108)"
    }, 
    {
        "hex": "#18A7B5", 
        "name": "Teal Blue", 
        "rgb": "(24, 167, 181)"
    }, 
    {
        "hex": "#EBC7DF", 
        "name": "Thistle", 
        "rgb": "(235, 199, 223)"
    }, 
    {
        "hex": "#FC89AC", 
        "name": "Tickle Me Pink", 
        "rgb": "(252, 137, 172)"
    }, 
    {
        "hex": "#DBD7D2", 
        "name": "Timberwolf", 
        "rgb": "(219, 215, 210)"
    }, 
    {
        "hex": "#17806D", 
        "name": "Tropical Rain Forest", 
        "rgb": "(23, 128, 109)"
    }, 
    {
        "hex": "#DEAA88", 
        "name": "Tumbleweed", 
        "rgb": "(222, 170, 136)"
    }, 
    {
        "hex": "#77DDE7", 
        "name": "Turquoise Blue", 
        "rgb": "(119, 221, 231)"
    }, 
    {
        "hex": "#FFFF66", 
        "name": "Unmellow Yellow", 
        "rgb": "(255, 255, 102)"
    }, 
    {
        "hex": "#926EAE", 
        "name": "Violet (Purple)", 
        "rgb": "(146, 110, 174)"
    }, 
    {
        "hex": "#324AB2", 
        "name": "Violet Blue", 
        "rgb": "(50, 74, 178)"
    }, 
    {
        "hex": "#F75394", 
        "name": "Violet Red", 
        "rgb": "(247, 83, 148)"
    }, 
    {
        "hex": "#FFA089", 
        "name": "Vivid Tangerine", 
        "rgb": "(255, 160, 137)"
    }, 
    {
        "hex": "#8F509D", 
        "name": "Vivid Violet", 
        "rgb": "(143, 80, 157)"
    }, 
    {
        "hex": "#FFFFFF", 
        "name": "White", 
        "rgb": "(255, 255, 255)"
    }, 
    {
        "hex": "#A2ADD0", 
        "name": "Wild Blue Yonder", 
        "rgb": "(162, 173, 208)"
    }, 
    {
        "hex": "#FF43A4", 
        "name": "Wild Strawberry", 
        "rgb": "(255, 67, 164)"
    }, 
    {
        "hex": "#FC6C85", 
        "name": "Wild Watermelon", 
        "rgb": "(252, 108, 133)"
    }, 
    {
        "hex": "#CDA4DE", 
        "name": "Wisteria", 
        "rgb": "(205, 164, 222)"
    }, 
    {
        "hex": "#FCE883", 
        "name": "Yellow", 
        "rgb": "(252, 232, 131)"
    }, 
    {
        "hex": "#C5E384", 
        "name": "Yellow Green", 
        "rgb": "(197, 227, 132)"
    }, 
    {
        "hex": "#FFAE42", 
        "name": "Yellow Orange", 
        "rgb": "(255, 174, 66)"
    }
]



function getHexColor(number)
{
	var rgb_array = random_colors_list[number]['hex'];
	return rgb_array;
}


