from django.shortcuts import render, get_object_or_404
from webservices import models
from webservices import util
from django.http import HttpResponse
import logging
import datetime
from django.core import serializers
import json

#grab out logger
logger = logging.getLogger(__name__)


def doAuth(request):

    if not 'HTTP_AUTHORIZATION' in request.META:
        return False

    token = request.META['HTTP_AUTHORIZATION']

    logger.info("Token is ", token)

    session = False
    try:
        session = models.Session.objects.get(token=token)
    except:
        return False

    logger.info("Got a session")

    if session:
        logger.info("User is ", session.user)
        request.session = session
        return True

    logger.info("No session no error")
    return False


def getVehicles(request):
    if not request.method == "GET":
        return HttpResponse("Bad method", status=400)

    if not doAuth(request):
        return HttpResponse(status=401)

    logger.info("Got user as ", request.session.user)

    my_vehicles = models.Vehicle.objects.filter(owner=request.session.user)
    return HttpResponse(json.dumps({
                                    'responseType' :    'vehiclesResponse',
                                    'vehicles' :        util.makeArray(my_vehicles)
                                    }))


def addGasStop(request):
    if not request.method == "POST":
        return HttpResponse("Bad Method", status=400)

    if not doAuth(request):
        return  HttpResponse(status=401)

    info = json.loads(request.body.decode('utf-8'))

    vehicle = get_object_or_404(models.Vehicle, pk=info['vehicle'], owner=request.session.user)

    gasStop = models.GasStop()

    gasStop.vehicle = vehicle
    gasStop.date = datetime.datetime.now()
    gasStop.fuel_purchased = info['gallonsPurchased']
    gasStop.odometer = info['odometer']
    gasStop.price = info['pricePaid']
    gasStop.latitude = info['userLocation']['lat']
    gasStop.longitude = info['userLocation']['lon']

    gasStop.save()

    return HttpResponse(json.dumps({
                            'responseType' : 'gasStopAddedResponse',
                            'result' : gasStop.toJSON()
                        }))
