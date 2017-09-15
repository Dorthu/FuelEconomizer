from django.shortcuts import get_object_or_404
from webservices import models
from webservices import util
from django.http import HttpResponse
import logging
import json
from django.utils import timezone
from .view_decorators import requires_authentication
from datetime import datetime

#grab our logger
logger = logging.getLogger(__name__)

def makeErrorResponse(errorMessage):
    return HttpResponse(json.dumps({
        'responseType': 'errorResponse',
        'errorMessage': errorMessage
    }), status=400)

@requires_authentication
def getVehicles(request):
    if not request.method == "GET":
        return HttpResponse("Bad method", status=400)

    my_vehicles = models.Vehicle.objects.filter(owner=request.session.user)
    return HttpResponse(json.dumps({
        'responseType' : 'vehiclesResponse',
        'vehicles': util.makeArray(my_vehicles),
    }))

@requires_authentication
def gasStop(request):
    """
    Recieves and routes requests to the /gasStop endpoint.

    :param request: The request from django.  Must be a GET or POST.
    :returns: The result of the function we route to.
    """
    if request.method == "POST":
        return _addGasStop(request)
    elif request.method == "GET":
        return _getGasStops(request)
    else:
        return HttpResponse(status=405)

def _addGasStop(request):
    """
    Accepts an add gas stop request and adds a Gas Stop for this vehicle if
    everything checks out.

    :param request: The request from django
    :returns: A gasStopAddedResponse with the new gasStop
    """
    if not request.method == "POST":
        return HttpResponse("Bad method", status=400)

    info = json.loads(request.body.decode('utf-8'))

    vehicle = get_object_or_404(models.Vehicle, pk=info['vehicle'],
                                owner=request.session.user)

    # Set up our new gas stop
    gasStop = models.GasStop()

    gasStop.vehicle = vehicle
    gasStop.date = timezone.now()
    gasStop.fuel_purchased = info['gallonsPurchased']
    gasStop.odometer = info['odometer']
    gasStop.price = info['pricePaid']
    gasStop.latitude = info['userLocation']['lat']
    gasStop.longitude = info['userLocation']['lon']

    # Let's make sure the data we got in is sane
    if float(gasStop.fuel_purchased) <= 0:
        return  makeErrorResponse("Fuel Purchased must be a positive number")

    if float(gasStop.fuel_purchased) > 99:
        return makeErrorResponse("Did you really buy more than 99 gallons of gas?")

    if float(gasStop.price) <= 0:
        return makeErrorResponse("Price must be a positive number")

    if float(gasStop.odometer) <= 0:
        return makeErrorResponse("Odometer reading must be a positive number")

    # If this vehicle had a previous gas stop, make sure the odometer is incrementing - no turning it back
    prevGasStop = models.GasStop.objects.filter(vehicle=gasStop.vehicle,
            date__lt=gasStop.date).order_by('-date')

    if prevGasStop and not float(gasStop.odometer) > prevGasStop.odometer:
        prevGasStop = prevGasStop[0]
        return makeErrorResponse("Previous odometer "
                "reading was "+str(prevGasStop.odometer)+" - you can't turn your "
                "odometer back!")

    # Everything checks out - let's do it!
    gasStop.save()

    return HttpResponse(json.dumps({
                            'responseType' : 'gasStopAddedResponse',
                            'result' : gasStop.toJSON()
                        }))

#From gasStop GET
def _getGasStops(request):
    total = int(request.GET['count']) if 'count' in request.GET else 10

    # Arbitrary limit is arbitrary
    if total > 10:
        total=10

    results = models.GasStop.objects.filter(vehicle__owner=request.session.user).order_by('-date')[:total]

    return HttpResponse(json.dumps({
        'responseType': 'gasStopsResponse',
        'values' : util.makeArray(results)
    }))

@requires_authentication
def getFuelEconomyReport(request):
    """
    This will return a detailed Fuel Economy Report.  The result can be saved for
    later pretty safely, as it won't change until the user inputs more data.

    :param request: passed from django
    :return: the report
    """
    #TODO: Don't return another unless the user has at least 3 gas stops
    if not request.method == "GET":
        return HttpResponse("Bad Method", status=400)

    report = {
        'vehicle': models.Vehicle.objects.filter(owner=request.session.user)[0],
        'responseType': 'fuelEconomyReportResponse'
    }

    total_gallons = total_miles = 0

    for gasStop in models.GasStop.objects.filter(vehicle=report['vehicle'])\
            .order_by('odometer')[1:]:
        total_gallons += gasStop.fuel_purchased

    total_miles = models.GasStop.objects.filter(vehicle=report['vehicle'])\
            .order_by('-odometer')[:1][0].odometer - \
        models.GasStop.objects.filter(vehicle=report['vehicle']).order_by('odometer')[:2][0].odometer

    report['average_mpg'] = "{0}".format(total_miles/total_gallons)

    first_stop = models.GasStop.objects.filter(vehicle=report['vehicle'])\
            .order_by('odometer')[0].date
    most_recent = models.GasStop.objects.filter(vehicle=report['vehicle'])\
            .order_by('-odometer')[0].date

    passed_time = most_recent - first_stop
    report['frequency'] = "{}".format(passed_time.days/len(models.GasStop.objects.filter(vehicle=report['vehicle'])))

    report['gasStops'] = util.makeArray(models.GasStop.objects\
            .filter(vehicle__owner=request.session.user)\
            .order_by('-date')[:10])
    report['vehicle'] = report['vehicle'].toJSON()

    return HttpResponse(json.dumps(report))
