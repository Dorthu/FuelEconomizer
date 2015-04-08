from django.shortcuts import render, get_object_or_404
from webservices import models
from django.http import HttpResponse
from django.core import serializers
import json
from .application_views import doAuth

def getUser(request):

    if not doAuth(request):
        return HttpResponse(status=401)

    user = request.session.user
    return HttpResponse(json.dumps(user.toJSON()))


def login(request):
    print("Login request")

    if not request.method == "POST":
        return HttpResponse("Please post", status=403)

    info = json.loads(request.body.decode('utf-8'))

    userEmail = info['email']
    password= info['password']

    try:
        user = models.User.objects.get(email=userEmail, password_hash=password)
    except:
        return HttpResponse(json.dumps({"responseType": "errorResponse", "errorMessage": "Invalid User/Password"}))
    session = models.Session()
    session.user = user
    return HttpResponse(json.dumps({"responseType":"loginResponse", "token":session.generateToken(user)}))


def getSession(token):
    return models.Session.objects.get(token=token)

