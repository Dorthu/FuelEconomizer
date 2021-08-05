from django.conf.urls import include, url
from django.contrib import admin
from webservices import urls as webserviceURLs

urlpatterns = [
    # Examples:
    # url(r'^$', 'fuelEconomizer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^api/v0/admin/', admin.site.urls),
    url(r'^api/v0/', include(webserviceURLs))
]
