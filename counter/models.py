from django.db import models
# Create your models here.

class App(models.Model):
  name = models.CharField(max_length=200)
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
