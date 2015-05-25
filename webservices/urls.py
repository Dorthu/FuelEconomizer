from django.conf.urls import patterns, url
from webservices import views

urlpatterns = patterns('',
                       url(r'^user/$', views.getUser, name="user"),
                       url(r'^vehicles/$', views.getVehicles, name="vehicles"),
                       url(r'^gasStop/$', views.gasStop, name="gasStop"),
                       url(r'^login/$', views.login, name="login"),
                       url(r'^resetPassword/$', views.resetPassword, name="resetPassword"),
                       )
