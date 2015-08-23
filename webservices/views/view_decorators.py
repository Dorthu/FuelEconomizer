from webservices.models import Session
from django.http import HttpResponse
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

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
        session = Session.objects.get(token=token)
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

def requires_authentication(view):

    # Do authentication on the view before processing it - and bail if they aren't logged in
    def authenticated_view(request):
        if not doAuth(request):
            return HttpResponse(status=401)
        return view(request)

    return authenticated_view
