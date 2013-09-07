from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
  user = models.ForeignKey(User, unique=True)
  apps = models.ManyToManyField('App')  

class App(models.Model):
  name = models.CharField(max_length=200)
  opens = models.IntegerField(default=0)
  clients   = models.ManyToManyField('Client')
  reports = models.ManyToManyField('Daily')

  def getDailyReport(self,date):
    return self.reports.get_or_create(date=date)[0]

class Daily(models.Model):
  date      = models.DateField(auto_now_add=True)
  clients   = models.ManyToManyField('Client')
  app_opens = models.IntegerField(default=0)

  def client_count(self): return self.clients.count()

class Client(models.Model):
  uid = models.CharField(max_length=200,primary_key=True)
  metadata = models.CharField(max_length=200,default="")

