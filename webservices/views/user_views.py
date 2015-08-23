from django.shortcuts import render, get_object_or_404
from webservices import models
from django.http import HttpResponse
from django.core import serializers
import json
from .view_decorators import requires_authentication
import hashlib
import base64
import uuid

@requires_authentication
def getUser(request):
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
        user = models.User.objects.get(email=userEmail)
    except:
        return HttpResponse(json.dumps({"responseType": "errorResponse", "errorMessage": "Invalid User/Password"}))

    if user.password_salt == 'CHANGEME':    # Old password authentication - not encrypted, this is going as soon as all accounts are fixed
        if user.password_hash != password:
            return HttpResponse(json.dumps({"responseType": 'errorResponse', 'errorMessage': 'Invalid User/Password'}))
    else:   # Real password authentication
        t_sha = hashlib.sha512();
        t_sha.update((password + user.password_salt).encode('utf-8'))

        if not user.password_hash == t_sha.hexdigest():
            return HttpResponse(json.dumps({"responseType": 'errorResponse', 'errorMessage': 'Invalid User/Password'}))

    # If we made it here, our creds checked out
    session = models.Session()
    session.user = user
    return HttpResponse(json.dumps({"responseType":"loginResponse", "token":session.generateToken(user)}))


def getSession(token):
    return models.Session.objects.get(token=token)

@requires_authentication
def resetPassword(request):
    try:
        info = json.loads(request.body.decode('utf-8'))
    except:
        return HttpResponse(status=400)

    if not info:
        return HttpResponse(status=400)

    user = request.session.user

    if not info['newPassword'] == info['confirmNewPassword']:
        return HttpResponse("{'responseType':'errorResponse', 'errorMessage':'Passwords don't match'}", status=400)

    # Generate the new password hash/salt
    user.password_salt = uuid.uuid4().hex
    password = info['newPassword']
    t_sha = hashlib.sha512()
    t_sha.update((password + user.password_salt).encode('utf-8'))
    user.password_hash = t_sha.hexdigest()

    # We don't need to reset our password anymore
    user.needs_password_reset = False

    # Save it
    user.save()

    # Invalidate all sessions
    models.Session.objects.filter(user=user).delete()

    # Return a new session token as if completing a login
    request.session = models.Session(user=user)
    return HttpResponse(json.dumps({"responseType":"loginResponse", "token":request.session.generateToken(user)}))