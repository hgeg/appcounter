from django.db import models
from django.contrib.auth.models import User
from datetime import date,timedelta
# Create your models here.

class Profile(models.Model):
  user = models.ForeignKey(User, unique=True)
  apps = models.ManyToManyField('App')  

class App(models.Model):
  name = models.CharField(max_length=200)
  opens = models.IntegerField(default=0)
  clients   = models.ManyToManyField('Client')
  reports = models.ManyToManyField('Daily')
  #actions   = models.ManyToManyField('Action')
  
  def getDailyReport(self,span):
    dt = date.today()-timedelta(days=7)
    report = self.reports.filter(date__gte=dt).order_by('date')
    indexed = []
    cliexed = []
    actixed = []
    if report:
      for d in span:
        t = report.filter(date=d['date'])
        if t: 
          indexed.append(t[0].app_opens)
          cliexed.append(t[0].clients.count())
          actixed.append(t[0].actions.all())
        else: 
          indexed.append(0)
          cliexed.append(9)
          actixed.append([])
    return [indexed, cliexed, actixed]

class Daily(models.Model):
  date      = models.DateField(auto_now_add=True)
  clients   = models.ManyToManyField('Client')
  app_opens = models.IntegerField(default=0)
  #actions   = models.ManyToManyField('Action')

  def client_count(self): return self.clients.count()

class Client(models.Model):
  uid = models.CharField(max_length=200,primary_key=True)

class Action(models.Model):
  clients  = models.ManyToManyField('Client')
  metadata = models.CharField(max_length=200)
  count    = models.IntegerField(default=0) 
  app      = models.CharField(max_length=200)

