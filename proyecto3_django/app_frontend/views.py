from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
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


def ayuda(request):
    context = {
        'timestamp': now().timestamp(),
    }
    return render(request, "ayuda.html", context)

def peticiones(request):
    context = {
        'timestamp': now().timestamp(),
    }
    return render(request, "peticiones.html", context)

def cargarXml(request):


    if request.method == 'POST' and request.FILES.get('xml_file'):
        archivo_xml = request.FILES['xml_file']
        files = {'archivo_xml': archivo_xml.read()}
        response = requests.post('http://127.0.0.1:5000/cargar_xml', files=files)

        if response.status_code == 200:
            xml_dataEntrada = archivo_xml.read().decode('utf-8')
            xml_dataEntrada = response.json().get('xml_content')
            print("-"*50)
            print("-"*50)
            request.session['xml_dataEntrada'] = xml_dataEntrada
            # request.session['xml_dataSalida'] = xml_dataSalida
        else:
            request.session['xml_dataEntrada'] = 'Error al procesar el archivo XML en el backend Flask.'
            # request.session['xml_dataSalida'] = None
        
        return redirect('home')	
    context = {
        'timestamp': now().timestamp(),
        'xml_dataEntrada': request.session.get('xml_dataEntrada'),
        # 'xml_dataSalida': xml_dataSalida,
    }
    return render(request, "cargarXml.html", context)

def home(request):
    if request.method == 'POST' and 'enviar' in request.POST:
        response = requests.post('http://127.0.0.1:5000/procesar_xml')
        if response.status_code == 200:
            request.session['xml_dataSalida'] = response.json().get('xml_content')
            print("Archivo XML procesado correctamente")
            return redirect('home')
        else:
            print("Error al procesar el archivo XML en el backend Flask esto es de carga F  ")
    
        
        
    context = {
        'timestamp': now().timestamp(),
        'xml_dataEntrada': request.session.get('xml_dataEntrada'), 
        'xml_dataSalida': request.session.get('xml_dataSalida'),
    }
    return render(request, "home.html", context)
