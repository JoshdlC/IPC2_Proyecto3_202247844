from django.shortcuts import render
from django.http import HttpResponse
from django.utils.timezone import now
import requests
import xml.etree.ElementTree as ET
import re

# Create your views here.
# def viewName(request):
# 	context = {}
# 	return render(request, "app_frontend/home.html", context)

def index(request):
    context = {
		'timestamp': now().timestamp(),
	}
    return render(request, "index.html", context)

def home(request):
    context = {
		'timestamp': now().timestamp(),
	}
    return render(request, "home.html", context)

def ayuda(request):
    context = {
        'timestamp': now().timestamp(),
    }
    return render(request, "ayuda.html", context)