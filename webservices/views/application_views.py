from django.shortcuts import get_object_or_404
from webservices import models
from webservices import util
from django.http import HttpResponse
import logging
import json
from django.utils import timezone

#grab out logger
logger = logging.getLogger(__name__)

def makeErrorResponse(errorMessage):
    return {
        'responseType': 'errorResponse',
        'errorMessage': errorMessage
    }

'''
 This function does a bit of "magic" - it checks the HTTP_AUTHORIZATION sent in with the request and validates the
 session, then drops the session into request.session and returns True.  If you call this and it returns True, you
 can safely assume that request.session is set and has a valid object matching the user who sent the request.  Yes,
 this is "spooky action at a distance," but it makes validation so clean and simple..I can't stop myself.
'''
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

        #update last_login
        session.last_login = timezone.now()
        session.save()

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
        return  HttpResponse(json.dumps(makeErrorResponse("Fuel Purchased must be a positive number")), status=400)

    if float(gasStop.fuel_purchased) > 99:
        return HttpResponse(json.dumps(makeErrorResponse("Did you really buy more than 99 gallons of gas?")))

    if float(gasStop.price) <= 0:
        return HttpResponse(json.dumps(makeErrorResponse("Price must be a positive number")), status=400)

    if float(gasStop.odometer) <= 0:
        return HttpResponse(json.dumps(makeErrorResponse("Odometer reading must be a positive number")), status=400)

    # If this vehicle had a previous gas stop, make sure the odometer is incrementing - no turning it back
    prevGasStop = False
    try:
        prevGasStop = models.GasStop.objects.filter(vehicle=gasStop.vehicle).filter(date__lt=gasStop.date).order_by('-date')[0]
    except:
        pass

    if prevGasStop:
        print("Previous odometer is "+str(prevGasStop.odometer)+" and current is "+str(gasStop.odometer))

    if prevGasStop and not float(gasStop.odometer) > prevGasStop.odometer:
        return HttpResponse(json.dumps(makeErrorResponse("Previous odometer reading was "+str(prevGasStop.odometer)+" - \
                you can't turn your odometer back!")), status=400)

    # Everything checks out - let's do it!
    gasStop.save()

    return HttpResponse(json.dumps({
                            'responseType' : 'gasStopAddedResponse',
                            'result' : gasStop.toJSON()
                        }))
