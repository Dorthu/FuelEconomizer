from django.conf.urls import patterns, url
from webservices import views

urlpatterns = patterns('',
                       url(r'^user/$', views.getUser, name="user"),
                       url(r'^vehicles/$', views.getVehicles, name="vehicles"),
                       url(r'^addGasStop/$', views.addGasStop, name="addGasStop"),
                       url(r'^login/$', views.login,
                           name="login"),
                       )
