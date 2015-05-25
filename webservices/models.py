from django.db import models
from datetime import datetime
import uuid

# Automobile Metadata
class Make(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Model(models.Model):
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    make = models.ForeignKey(Make)

    def __str__(self):
        return str(self.year) + " " + str(self.make) + " " + self.name


# User Metadata
class User(models.Model):
    #User Fields
    email = models.EmailField(max_length=75)
    password_hash = models.TextField()
    password_salt = models.TextField()
    name = models.CharField(max_length=75)
    needs_password_reset = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def toJSON(self):
        return {
            'name':                 self.name,
            'email':                self.email,
            'needsPasswordReset':   self.needs_password_reset
        }


class Session(models.Model):
    #User
    user = models.ForeignKey(User)

    #Login Info
    initial_login = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField()

    #Token
    token = models.CharField(max_length=75)

    def __str__(self):
        return "User " + str(self.user) + " session, last login " + str(self.last_login)

    def generateToken(self, user):
        self.token = uuid.uuid1().hex;
        self.update()
        return self.token

    def update(self):
        self.last_login = datetime.now()
        self.save()
        print("Saved token " + self.token)


#Vehicle Metadata
class Vehicle(models.Model):
    #Associations
    owner = models.ForeignKey(User)
    model = models.ForeignKey(Model)
    default = models.BooleanField(default=False)

    def __str__(self):
        return str(self.owner) + "'s " + str(self.model)

    def toJSON(self):
        return {
            'owner':   str(self.owner),
            'model':   str(self.model),
            'default': str(self.default),
            'display': str(self),
            'vid' :    self.pk
        }


# Fuel Usage Data
class GasStop(models.Model):
    #Associations
    vehicle = models.ForeignKey(Vehicle)

    #Implied Fields
    date = models.DateTimeField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    #Express Fields
    odometer = models.IntegerField()
    fuel_purchased = models.DecimalField(max_digits=6, decimal_places=4)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return str(self.vehicle) + " : Gas Stop at " + str(self.odometer) + " miles"

    def __getattr__(self, attr):
        if attr == 'price_per_gallon':
            return float(self.price) / float(self.fuel_purchased)
        elif attr == 'miles_per_gallon':
            prev_stop = False
            try:
                prev_stop = GasStop.objects.filter(vehicle=self.vehicle).filter(date__lt=self.date).order_by('-date')[0]
            except:
                pass
            if prev_stop:
                return (float(self.odometer) - prev_stop.odometer) / float(self.fuel_purchased)
            return "Not Enough Data"
        else:
            raise AttributeError


    def toJSON(self):
        return {
            'vehicle' :        self.vehicle.toJSON(),
            'datetime' :       str(self.date),
            'lat' :            str(self.latitude),
            'lon' :            str(self.longitude),
            'odometer' :       self.odometer,
            'fuelPurchased':   str(self.fuel_purchased),
            'pricePaid' :      str(self.price),
            'pricePerGallon':  str(self.price_per_gallon),
            'milesPerGallon':  str(self.miles_per_gallon)
        }
