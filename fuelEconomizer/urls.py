from django.conf.urls import patterns, include, url
from django.contrib import admin
from webservices import urls as webserviceURLs

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'fuelEconomizer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^webservices/', include(webserviceURLs))
)
