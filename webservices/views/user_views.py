from django.shortcuts import render, get_object_or_404
from webservices import models
from django.http import HttpResponse
from django.core import serializers
import json


def getUser(request, token):
    session = get_object_or_404(models.Session, token=token)
    user = session.user.getJSON()
    return HttpResponse(user)


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

