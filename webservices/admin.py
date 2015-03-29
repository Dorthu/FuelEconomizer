from django.contrib import admin
from webservices.models import *

# Register your models here.
class MakeAdminObj(admin.ModelAdmin):
    field = ['name']


class ModelAdminObj(admin.ModelAdmin):
    field = ['make', 'name', 'year']


class UserAdminObj(admin.ModelAdmin):
    field = ['email', 'name']


class VehicleAdminObj(admin.ModelAdmin):
    field = ['owner', 'model']


class GasStopAdminObj(admin.ModelAdmin):
    field = ['vehicle', 'date', 'latitude', 'longitude', 'odometer', 'fuel_purchased', 'price']


class SessionAdminObj(admin.ModelAdmin):
    field = ['user', 'token']


admin.site.register(Make, MakeAdminObj)
admin.site.register(Model, ModelAdminObj)
admin.site.register(User, UserAdminObj)
admin.site.register(Vehicle, VehicleAdminObj)
admin.site.register(GasStop, GasStopAdminObj)
admin.site.register(Session, SessionAdminObj)
