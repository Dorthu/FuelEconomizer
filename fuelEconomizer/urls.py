from django.conf.urls import patterns, include, url
from django.contrib import admin
from webservices import urls as webserviceURLs

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'fuelEconomizer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^api/v0/admin/', include(admin.site.urls)),
    url(r'^api/v0/', include(webserviceURLs))
)
