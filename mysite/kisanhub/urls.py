from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'getTransformerList$', views.get_top_info, name='get_top_info'),
    url(r'^getReportChartData$',views.get_reportsummary_data,name='get_reportsummary_data'),
    url(r'^load_dat_from_web$',views.Check_Data_From_Web,name='Check_Data_From_Web'),
]