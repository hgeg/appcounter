from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'counter.views.home', name='home'),
    # url(r'^appcounter/', include('appcounter.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')/,

    # Uncomment the next line to enable the admin:
    url(r'^appcounter/admin/', include(admin.site.urls)),
    url(r'^appcounter/add/(?P<uid>.*)/(?P<app>.*)/', 'counter.views.open', name='add'),
    url(r'^appcounter/action/(?P<uid>.*)/(?P<app>.*)/(?P<action>.*)/', 'counter.views.action', name='add'),
    url(r'^appcounter/next/', 'counter.views.next_day', name='next'),
    url(r'^appcounter/login/', 'counter.views.login', name='login'),
    url(r'^accounts/login/', 'counter.views.login', name='login'),
    url(r'^appcounter/logout/', 'counter.views.login', name='logout'),
    url(r'^appcounter/report/', 'counter.views.report', name='report'),
    url(r'^appcounter/app/(?P<app>.*)/', 'counter.views.detail', name='add'),
    url(r'^appcounter/', 'counter.views.report', name='report'),
)
