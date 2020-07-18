from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from errands.models import Errand, Piece
from datetime import datetime as dt, timedelta as td
from django.urls import reverse
from django.http import HttpResponsePermanentRedirect as httpRPR, HttpResponse as httpR
from home.std import Std
import json


def home(request):
    # Accessible to all
    return render(request, 'home/home.html')


def in_session(request):
    if request.session.get(Std.Keys.user_logged_in, False):
        return True
    else:
        return False


def login(request):
    if request.method == 'POST':
        # If User Identity is correct
        if request.POST[Std.Keys.identity] == Std.user_identity:
            # Start Session
            request.session[Std.Keys.user_logged_in] = True
            # Redirect to Client if exists
            if Std.Keys.client_site in request.POST:
                return httpRPR(request.POST[Std.Keys.client_site])
            # Else Redirect to home
            else:
                return httpRPR(reverse('errands:all_errands'))
        # Else
        else:
            return render(request, 'home/invalid_access.html')
    else:
        # Login Page
        return render(request, 'home/login.html')


def logout(request):
    # End Session
    request.session[Std.Keys.user_logged_in] = False
    return httpR(json.dumps({'message': 'Safe Mode Activated'}))
