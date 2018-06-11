from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView
from django.conf import settings
from django.http.response import HttpResponse, JsonResponse
import requests
import datetime
import json
import pprint
from .models import Employees, LogTimes, Organizations, Projects
from django.db.models import Q
from django.core.mail import EmailMessage
import csv

# Create your views here.

class TrackedTimeView(ListView):

    model = LogTimes
    context_object_name = "tracked_time_list"

    def get_context_data(self, *args, **kwargs):
        context = super(TrackedTimeView, self).get_context_data(*args, **kwargs)

        date_filter = self.request.GET.get('date-filter')
        if date_filter is not None and len(date_filter) > 0:
            date_filter_obj = datetime.datetime.strptime(date_filter, "%Y-%m-%d")
        else:
            date_filter_obj = datetime.date.today() - datetime.timedelta(1)

        represent_date = date_filter_obj.strftime("%Y-%m-%d")
        
        activated= LogTimes.objects.filter(log_date=date_filter_obj).exclude(logged_time="0:00:00")
        context['users'] = remove_duplicate_user(activated)
        context['projects'] = remove_duplicate_project(activated)

        context['datetime'] = represent_date
        context['datefilter'] = self.request.GET.get('date-filter')
        return context

    def get_queryset(self):
        # original qs
        qs = super().get_queryset() 
        # filter by a variable captured from url, for example
        date_filter = self.request.GET.get('date-filter')
        
        if date_filter is not None and len(date_filter) > 0 :
            date_filter_obj = datetime.datetime.strptime(date_filter, "%Y-%m-%d")
        else:
            date_filter_obj = datetime.date.today() - datetime.timedelta(1)

        return qs.filter(log_date=date_filter_obj).order_by('project_id')


def remove_duplicate_user(duplicate):
    final_list = []
    namelist = []
    for num in duplicate:
        if num.user_id.name not in namelist:
            final_list.append(num)
            namelist.append(num.user_id.name)
    return final_list


def remove_duplicate_project(duplicate):
    final_list = []
    namelist = []
    for num in duplicate:
        if num.project_id.name not in namelist:
            final_list.append(num)
            namelist.append(num.project_id.name)
    return final_list


def send_mail_to_manger():
    pass


def save_output(request):
    filter_date_str = ""
    if request.method == 'POST':
        filter_date_str = request.POST.get('filter_date', '')
        filter_date = filter_date_str.replace('\n', '')
        filter_date = filter_date.lstrip()

        if filter_date is not "None" and len(filter_date) > 0 :
            filter_date_obj = datetime.datetime.strptime(filter_date, "%Y-%m-%d")
        else:
            filter_date_obj = datetime.datetime.today() - datetime.timedelta(1)
    
    activated= LogTimes.objects.filter(log_date=filter_date_obj).exclude(logged_time="0:00:00")

    users = remove_duplicate_user(activated)
    projects = remove_duplicate_project(activated)

    outputlists = []
    
    log_date = ["Date", filter_date_str]
    outputlists.append(log_date)

    headerrow = ['']
    for user in users:
         headerrow.append(user.user_id.name)
    outputlists.append(headerrow)

    for project in projects:
        outputlist = []
        outputlist.append(project.project_id.name)
        for user in users:
            for activity in activated:
                if activity.user_id.id is user.user_id.id and activity.project_id.id is project.project_id.id:
                    outputlist.append(activity.logged_time)
        outputlists.append(outputlist)
    response_data = {
        'status': '404'
    }
    with open('output.csv', 'w') as outputFile:
        outputWriter = csv.writer(outputFile)
        outputWriter.writerows(outputlists)
        response_data = {
            'status': '200',
            'data': outputlists,
        }

    return JsonResponse(response_data)


def retrieve_hub_res(self):
    auth_token = retrieve_auth_info()
    
    organlists = retrieve_organization(auth_token=auth_token)

    tracks_list = []
    for organ in organlists:
        
        projects = retrieve_projects(auth_token, str(organ))
        members = retrieve_members(auth_token, str(organ))
        track_org_list = []
        for project in projects:
            track_proj_list = []
            for member in members:
                track_time = retrieve_activities(auth_token, str(member), str(project))
                track_proj_list.append(track_time)
            track_org_list.append(track_proj_list)
        tracks_list.append(track_org_list)
    
    return HttpResponse(tracks_list)
    
    
def retrieve_auth_info():
    # if settings.HUBSTAFF_APP_TOKEN and settings.HOST_EMAIL and settings.HOST_PASS:
    auth_endpoint = settings.HUBSTAFF_ENDPOINT + 'auth'

    headers = {'App-token': settings.HUBSTAFF_APP_TOKEN}

    data = {
        'email': settings.HOST_EMAIL,
        'password': settings.HOST_PASS 
    }

    re = requests.post(url=auth_endpoint, headers=headers, data=data)

    auth_info = json.loads(re.text)['user']
    
    return auth_info['auth_token']


def retrieve_organization(auth_token):

    organization_endpoint = settings.HUBSTAFF_ENDPOINT + 'organizations'

    headers = {
        'Auth-token': auth_token,
        'App-token': settings.HUBSTAFF_APP_TOKEN
    }

    re = requests.get(url=organization_endpoint, headers=headers)

    organs = json.loads(re.text)['organizations']
    organ_ids = []

    for organ in organs:
        num_results = Organizations.objects.filter(organization_id= organ['id']).count()
        organ_ids.append(organ['id'])
        if num_results == 0:
            o = Organizations(organization_id=organ['id'],name=organ['name'])
            o.save()

    return organ_ids


def retrieve_projects(auth_token, organization_id):
    projects_endpoint = settings.HUBSTAFF_ENDPOINT + 'organizations/' + organization_id + '/projects'

    headers = {
        'Auth-token': auth_token,
        'App-token': settings.HUBSTAFF_APP_TOKEN,
    }

    re = requests.get(url=projects_endpoint, headers=headers)

    projs = json.loads(re.text)['projects']
    proj_list = []

    organ = Organizations.objects.get(organization_id=organization_id)

    for proj in projs:
        num_results = Projects.objects.filter(project_id= proj['id']).count()
        proj_list.append(proj['id'])
        if num_results == 0:
            
            p = Projects(project_id=proj['id'], 
                         name=proj['name'], 
                         status=proj['status'], 
                         description=proj['description'], 
                         organization_id=organ
            )
            p.save()
    
    return proj_list


def retrieve_members(auth_token, organization_id):
    members_endpoint = settings.HUBSTAFF_ENDPOINT + 'organizations/'+ organization_id + '/members'

    headers = {
        'Auth-token': auth_token,
        'App-token': settings.HUBSTAFF_APP_TOKEN,
    }

    re = requests.get(url=members_endpoint, headers=headers)

    members = json.loads(re.text)['users']
    member_list = []

    organ = Organizations.objects.get(organization_id=organization_id)

    for member in members:
        num_results = Employees.objects.filter(employee_id= member['id']).count()
        member_list.append(member['id'])
        if num_results == 0:
            m = Employees(
                employee_id=member['id'], 
                name=member['name'], 
                email=member['email'], 
                organization_id=organ
            )
            m.save()
    
    return member_list
    

def retrieve_activities(auth_token, user_id, project_id):
    activities_endpoint = settings.HUBSTAFF_ENDPOINT + 'activities/'

    yesterday = datetime.date.today() - datetime.timedelta(1)
    started_time = yesterday.strftime("%Y-%m-%d %H:%M:%S")

    end_time = yesterday.strftime("%Y-%m-%d") + " 23:59:59"

    headers = {
        'Auth-token': auth_token,
        'App-token': settings.HUBSTAFF_APP_TOKEN,
        
    }

    query_string = {
        'start_time': started_time,
        'stop_time': end_time,
        'projects': project_id,
        'users': user_id
    }

    re = requests.get(url=activities_endpoint, headers=headers, params=query_string)

    user = get_object_or_404(Employees, employee_id=user_id)
    project = get_object_or_404(Projects, project_id=project_id)

    activities = json.loads(re.text)['activities']

    total_tracked = 0;

    for activity in activities:
        total_tracked += int(activity['tracked'])
    
    num_results = LogTimes.objects.filter(
                            project_id= project_id, 
                            user_id = user_id, 
                            log_date = yesterday
    ).count()
        
    if num_results == 0:
        l = LogTimes(project_id=project, 
                     user_id=user, 
                     log_date=yesterday, 
                     logged_time = str(datetime.timedelta(seconds=total_tracked))
        )
        l.save()
    return total_tracked

