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
            data = response.json()
            xml_dataEntrada = data.get('xml_content')
            fileIndex = data.get('fileIndex')
            request.session['xml_dataEntrada'] = xml_dataEntrada
            request.session['fileIndex'] = fileIndex
        else:
            request.session['xml_dataEntrada'] = 'Error al procesar el archivo XML en el backend Flask. CARGA'
        
        return redirect('home')
    
    context = {
        'timestamp': now().timestamp(),
        'xml_dataEntrada': request.session.get('xml_dataEntrada'),
    }
    return render(request, "cargarXml.html", context)


def home(request):
    
    if request.method == 'POST':
        if 'enviar' in request.POST:
            fileIndex = request.session.get('fileIndex')
            response = requests.post('http://127.0.0.1:5000/procesar_xml', json={'fileIndex': fileIndex})
            if response.status_code == 200:
                data = response.json()
                request.session['xml_dataSalida'] = data.get('salida_xml_content')
                request.session['sentimientos_positivos'] = data.get('sentimientos_positivos', [])
                request.session['sentimientos_negativos'] = data.get('sentimientos_negativos', [])

                print("Archivo XML procesado correctamente")
                return redirect('home')
            else:
                print("Error al procesar el archivo XML en el backend Flask en procesar_xml")
                print(response.text)
        elif 'reset' in request.POST:
            response = requests.post('http://127.0.0.1:5000/reset')
            if response.status_code == 200:
                print("Reset realizado correctamente")
                request.session['xml_dataEntrada'] = None
                request.session['xml_dataSalida'] = None
                request.session['sentimientos_positivos'] = []
                request.session['sentimientos_negativos'] = []
                return redirect('home')
            else:
                print("Error al realizar el reset en el backend Flask")
                print(response.text)
            
            
    context = {
        'timestamp': now().timestamp(),
        'xml_dataEntrada': request.session.get('xml_dataEntrada'),
        'xml_dataSalida': request.session.get('xml_dataSalida'),
        'sentimientos_positivos': request.session.get('sentimientos_positivos', []),
        'sentimientos_negativos': request.session.get('sentimientos_negativos', []),
    }
    return render(request, "home.html", context)