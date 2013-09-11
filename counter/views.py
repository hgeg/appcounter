# Create your views here.
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
from django.contrib.auth import login as authLogin 
from django.contrib.auth import logout as authLogout
from django.http import HttpResponse,HttpResponseRedirect
from counter.models import *
from datetime import date,timedelta
import json

def open(request,uid,app):
  currentApp = App.objects.get_or_create(name=app)[0]
  today = currentApp.reports.get_or_create(date=date.today())[0]
  client = Client.objects.get_or_create(uid=uid)[0]
  today.clients.add(client)
  currentApp.clients.add(client)
  today.app_opens += 1
  currentApp.opens += 1
  today.save()
  currentApp.save()
  return HttpResponse('OK')

def action(request,uid,app,action):
  #get objects
  currentApp = App.objects.get_or_create(name=app)[0]
  today = currentApp.reports.get_or_create(date=date.today())[0]
  client = Client.objects.get_or_create(uid=uid)[0]
  action = Action.objects.get_or_create(metadata=action,appname=app)[0]
  action.counts +=1;
  action.save()

  #add client
  today.clients.add(client)
  currentApp.clients.add(client)

  #add action
  currentApp.actions.add(action)
  today.actions.add(action)
  client.actions.add(action)
 
  today.save()
  currentApp.save()
  return HttpResponse('OK')

def next_day(request):
  for e in App.objects.all(): e.reports.get_or_create(date=date.today())
  return HttpResponse('OK')

@login_required
def report(request):
  span = Daily.objects.order_by('date').values('date').distinct()
  profile = request.user.get_profile()
  apps = profile.apps.all()
  opens = {}
  clients = {}
  for app in apps:
      #actions are unused at this point
      opens[app.name],clients[app.name], x = app.getDailyReport(span)
  return render_to_response('report.html',{'opens':opens,'clients':clients,'span':span,'apps':apps})

@login_required
def detail(request,app):
  span = Daily.objects.order_by('date').values('date').distinct()
  profile = request.user.get_profile()
  currentApp = profile.apps.filter(name=app)
  if not currentApp:
    return render_to_response('error.html',{'msg':'You don\'t have the permissions to see this app.'})
  currentApp = currentApp[0]
  data = currentApp.getDailyReport(span)
  return render_to_response('detail.html',{'opens':data[0],'clients':data[1],'actions':data[2],'span':span,'app':currentApp})
  
def login(request):
  if request.method != 'POST':
    return render_to_response('signin.html',{},context_instance=RequestContext(request))
  else:
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
      if user.is_active:
        authLogin(request,user)
        profile = Profile.objects.get_or_create(user=user)
        return HttpResponseRedirect('/appcounter/report/')
      else:
        return render_to_response('signin.html',{'message':'User deactivated'},context_instance=RequestContext(request))
    else:
      return render_to_response('signin.html',{'message':'Incorrect username/password'},context_instance=RequestContext(request))


@login_required
def logout(request):
  authLogout(request)
  return render_to_response('signin.html',{'message':'Logout Successful'})

