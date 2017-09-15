from django.conf.urls import url
from webservices import views

urlpatterns = [
        url(r'^user/$', views.getUser, name="user"),
        url(r'^vehicles/$', views.getVehicles, name="vehicles"),
        url(r'^gasStop/$', views.gasStop, name="gasStop"),
        url(r'^fuelEconomyReport/$', views.getFuelEconomyReport, name="fuelEconomyReport"),
        url(r'^login/$', views.login, name="login"),
        url(r'^resetPassword/$', views.resetPassword, name="resetPassword"),
]
