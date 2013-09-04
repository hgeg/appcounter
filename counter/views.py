# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
from django.contrib.auth import login as authLogin 
from django.contrib.auth import logout as authLogout
from django.http import HttpResponse
from counter.models import *
from datetime import date,timedelta

def add(request,uid,app):
  currentApp = App.objects.get_or_create(name=app)[0]
  today = currentApp.getDailyReport(date.today())
  print today
  client = Client.objects.get_or_create(uid=uid,defaults={'metadata':'{"app":"%s"}'%app})[0]
  today.clients.add(client)
  today.app_opens +=1
  today.save()
  return HttpResponse('OK')

@login_required
def report(request,app):
  apps = App.objects.all()
  data = {}
  for app in apps:
    report = []
    dt = date.today()-timedelta(days=7)
    report = app.reports.filter(date__gte=dt).order_by('date')
    if report:
      data[app.name] = report
    else: data[app.name] = None
  span = Daily.objects.order_by('date') 
  return render_to_response('report.html',{'data':data,'span':span})

def login(request):
  if request.method != 'POST':
    return render_to_response('signin.html')
  else:
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
      if user.is_active:
        authLogin(request,user)
        return report(request,'all')
      else:
        return render_to_response('signin.html',{'message':'User deactivated'})
    else:
      return render_to_response('signin.html',{'message':'Incorrect username/password'})


@login_required
def logout(request):
  authLogout(request)
  return render_to_response('signin.html',{'message':'Logout Successful'})

