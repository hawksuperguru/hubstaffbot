from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^activities/$', views.retrieve_hub_res, name='retrieve_activities'),
    # url(r'^timesheet/$', views.LogTimeList.as_view(), name='retrieve_activities'),
    url(r'^$', views.TrackedTimeView.as_view(), name='view_timesheet'),
    url(r'^output/$', views.save_output, name='save_output'),
]