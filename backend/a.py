from flask import Flask, request, jsonify, session
import xml.etree.ElementTree as ET
import os
from werkzeug.utils import secure_filename
import re

from empresa import Empresa, Servicio
from diccionarioSent import DiccionarioSent
from mensaje import Mensaje
from analizador import Analizador

import requests

app = Flask(__name__)
app.secret_key = 'supersecretkey'
xml_dataEntrada = None
xml_dataSalida = None

baseDeDatosFalsa = {
    "data": []
}
           
#* si no existe la carpeta de subidas        
if not os.path.exists('uploads'):
    os.makedirs('uploads') 
    
empresasGlobal = []
serviciosGlobal = []
diccionario = []
sentimientosPositivo = []
sentimientosNegativo = []
sentimientoX = []
mensajesGlobal = []

def quitarTildes(palabra):
    reemplazos = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("Á", "a"),
        ("É", "e"),
        ("Í", "i"),
        ("Ó", "o"),
        ("Ú", "u")
    )           
    
    for a, b in reemplazos:
        palabra = palabra.replace(a, b)
                   
    return palabra


# def cargarArchivo():
#     files = request.files.getlist('files')
    
    
#     for file in files:
#         if file:
#            fileName = secure_filename(file.filename)
#            filePath = os.path.join('uploads', fileName)
#            file.save(filePath)
           
#            procesarArchivo(filePath)
           
           
def procesarArchivo(filePath):
    global sentimientosNegativo
    global sentimientosPositivo
    global sentimientoX
    global mensajesGlobal
    
    
    tree = ET.parse(filePath)
    root = tree.getroot()
    xml_content = ET.tostring(root, encoding='unicode')

    session['xml_content'] = xml_content
    print("Se comienza el proceso del archivo")
    
    for diccionario in root.findall("diccionario"):
        for sentiemtoPos in diccionario.findall("sentimientos_positivos"):
            palabra = sentiemtoPos.text.strip().lower() #* Se convierte a minúsculas
            palabra = quitarTildes(palabra)
            sentimientosPositivo.append(palabra)
            
        for sentiemtoNeg in diccionario.findall("sentimientos_negativos"):
            palabra = sentiemtoNeg.text.strip().lower()
            palabra = quitarTildes(palabra)
            sentimientosNegativo.append(palabra)
            
        for sentimientoX in diccionario.findall("sentimientos_neutros"):
            palabra = sentimientoX.text.strip().lower()
            palabra = quitarTildes(palabra)
            sentimientoX.append(palabra)   
            
        #! Busca empresas y servicios
        for empresas in root.findall("empresa"):
            nombreEmpresa = empresas.find("nombre").text.strip()
            
            print("Nombre de la empresa: ", nombreEmpresa)
            
            #* revisa si ya existe la empresa
            empresaExistente = None
            nodoEmpresa = None
            while nodoEmpresa != None:
                if nodoEmpresa.data["nombre"] == nombreEmpresa:
                    empresaExistente = nodoEmpresa.data
                    break
                nodoEmpresa = nodoEmpresa.next
            
            if empresaExistente:
                empresa = empresaExistente
            else:
                empresa = Empresa(nombreEmpresa)
                empresasGlobal.append(empresa)
                
            #* Recorre servicios
            for servicios in empresas.find("servicios"):
                for servicio in servicios.findall("servicio"):
                    nombreServicio = servicio.get("nombre").text.strip()
                    aliasServicio = servicio.findall("alias").text.strip()
                    
                    #* revisa si ya existe el servicio
                    servicioExistente = None
                    nodoServicio = empresa.servicios.head
                    while nodoServicio != None:
                        if nodoServicio.data["nombre"] == nombreServicio:
                            servicioExistente = nodoServicio.data
                            break
                        nodoServicio = nodoServicio.next
                    
                    if servicioExistente:
                        servicio = servicioExistente
                    else:
                        servicio = Servicio(nombreServicio, aliasServicio)
                        empresa.servicios.append(servicio)
                        serviciosGlobal.append(servicio)
    
    for mensajes in root.findall("lista_mensajes"):
        
        mensaje = mensajes.find("mensaje").text.strip()
        
        #* Busca la fecha con un regex
        regexFecha = re.compile(r'\b(0[1-9]|[12]\d|3[01])[-/](0[1-9]|1[0-2])[-/](19\d\d|20\d\d)\b')
        fecha = regexFecha.search(mensaje)
        #! Hay q validar la fecha
        print("Fecha: ", fecha)
        
        regexUser = re.compile(r'Usuario:\s*([a-zA-Z0-9]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})')       
        usuario = regexUser.search(mensaje)
        print("Usuario: ", usuario)
         
        regexRed = re.compile(r'Red social:\s*([\w\s]+)')
        redSocial = regexRed.search(mensaje)
        print("Red social: ", redSocial)
        
        contenido = mensaje
        
        mensajeCompleto = Mensaje(fecha, usuario, redSocial, contenido)
        mensajesGlobal.append(mensajeCompleto)
        
        # texto = mensaje.find("texto").text.strip()
        # fecha = mensaje.find("fecha").text.strip()
        # hora = mensaje.find("hora").text.strip()
        # empresa = mensaje.find("empresa").text.strip()
        # servicio = mensaje.find("servicio").text.strip()
        
        # mensaje = Mensaje(texto, fecha, hora, empresa, servicio)
        # empresa = None
        # servicio = None
        
        # #* Busca la empresa
        # for empresa in empresasGlobal:
        #     if empresa.nombre == mensaje.empresa:
        #         break
        
        # #* Busca el servicio
        # for servicio in serviciosGlobal:
        #     if servicio.nombre == mensaje.servicio:
        #         break
        
        # #* Agrega el mensaje al servicio
        # servicio.mensajes.append(mensaje)                
                


    

@app.route('/')
def home():
    return "Servidor Flask está corriendo"

@app.route('/cargar_xml', methods=['POST'])
def cargar_xml():

    
    if 'archivo_xml' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo XML'}), 400

    archivo_xml = request.files['archivo_xml']
    fileName = secure_filename(archivo_xml.filename)
    filePath = os.path.join('uploads', fileName)
    archivo_xml.save(filePath)
    
 

    return jsonify({'message': 'Archivo xml cargado correctamente'})

@app.route('/procesar_xml', methods=['POST'])
def procesar_xml():
    filePath = session.get('filePath')
    if not filePath:
        return jsonify({'error': 'No se ha cargado ningún archivo XML'}), 400
    
    #* Procesar el archivo
    procesarArchivo(filePath)
    tree = ET.parse(filePath)
    root = tree.getroot()
    xml_content = ET.tostring(root, encoding='unicode')
    
    return jsonify({'xml_content': xml_content})


if __name__ == '__main__':
    app.run(debug=True)
    
    
    
def procesarArchivo(filePath):
    global sentimientosNegativo
    global sentimientosPositivo
    global sentimientoX
    global mensajesGlobal
    global mensajesPositivos
    global mensajesNegativos
    global mensajesNeutros
    global totalPositivos
    global totalNeg
    global TotalX
    
    tree = ET.parse(filePath)
    root = tree.getroot()
    xml_content = ET.tostring(root, encoding='unicode')

    session['xml_content'] = xml_content
    print("Se comienza el proceso del archivo")
    
    for diccionario in root.findall("diccionario"):
        for sentiemtoPos in diccionario.findall("sentimientos_positivos/palabra"):
            palabra = sentiemtoPos.text.strip().lower() #* Se convierte a minúsculas
            palabra = quitarTildes(palabra)
            sentimientosPositivo.append(palabra)
            
        for sentiemtoNeg in diccionario.findall("sentimientos_negativos/palabra"):
            palabra = sentiemtoNeg.text.strip().lower()
            palabra = quitarTildes(palabra)
            sentimientosNegativo.append(palabra)
            
        for sentimientoX in diccionario.findall("sentimientos_neutros/palabra"):
            palabra = sentimientoX.text.strip().lower()
            palabra = quitarTildes(palabra)
            sentimientoX.append(palabra)   
            
        #! Busca empresas y servicios
        for empresas in diccionario.findall("empresas_analizar/empresa"):
            nombreEmpresa = empresas.find("nombre").text.strip()
            
            print("Nombre de la empresa: ", nombreEmpresa)
            
            #* revisa si ya existe la empresa
            empresaExistente = None
            for empresa in empresasGlobal:
                if empresa.nombre == nombreEmpresa:
                    empresaExistente = empresa
                    break
            
            if empresaExistente:
                empresa = empresaExistente
            else:
                empresa = Empresa(nombreEmpresa)
                empresasGlobal.append(empresa)
                
            #* Recorre servicios
            for servicio in empresas.findall("servicio"):
                nombreServicio = servicio.get("nombre").strip()
                aliasServicio = [alias.text.strip() for alias in servicio.findall("alias")]
                
                #* revisa si ya existe el servicio
                servicioExistente = None
                for serv in empresa.servicios:
                    if serv.nombre == nombreServicio:
                        servicioExistente = serv
                        break
                    
                if servicioExistente:
                    servicio = servicioExistente
                else:
                    servicio = Servicio(nombreServicio, aliasServicio)
                    empresa.servicios.append(servicio)
                    serviciosGlobal.append(servicio)
    
    for mensaje_element in root.findall("lista_mensajes/mensaje"):
        
        mensaje = mensaje_element.text.strip()
        
        #* Busca la fecha con un regex
        regexFecha = re.compile(r'\b(0[1-9]|[12]\d|3[01])[-/](0[1-9]|1[0-2])[-/](19\d\d|20\d\d)\b')
        fecha = regexFecha.search(mensaje)
        fecha_text = fecha.group() if fecha else "Fecha no encontrada"
        print("Fecha: ", fecha_text)
        
        regexUser = re.compile(r'Usuario:\s*(@?[a-zA-Z0-9_.#]+(?:@[a-zA-Z0-9_.-]+)?)')       
        usuario = regexUser.search(mensaje)
        usuario_text = usuario.group(1) if usuario else "Usuario no encontrado"
        print("Usuario: ", usuario_text)

        regexRed = re.compile(r'Red social:\s*([A-Za-z]+)')
        redSocial = regexRed.search(mensaje)
        redSocial_text = redSocial.group(1) if redSocial else "Red social no encontrada"
        print("Red social: ", redSocial_text)
            
        contenido = mensaje
        
        mensajeCompleto = Mensaje(fecha_text, usuario_text, redSocial_text, contenido)
        
        #* Clasificar los mensajes
        mensajeClasi = False
        contenidoLowerSinTildes = quitarTildes(contenido.lower())
        
        for palabra in sentimientosPositivo:
            if palabra in contenidoLowerSinTildes:
                mensajesPositivos.append(mensajeCompleto)
                totalPositivos += 1
                mensajeClasi = True
                break
            
        if not mensajeClasi:
            for palabra in sentimientosNegativo:
                if palabra in contenidoLowerSinTildes:
                    mensajesNegativos.append(mensajeCompleto)
                    totalNeg += 1
                    mensajeClasi = True
                    break
                
        if not mensajeClasi:
            mensajesNeutros.append(mensajeCompleto)
            TotalX += 1
            
        mensajesGlobal.append(mensajeCompleto)
        
        

def generarSalida():
    salidaXml = ET.Element("lista_respuestas")
    
    # Agrupar mensajes por fecha
    mensajes_por_fecha = {}
    for mensaje in mensajesGlobal:
        if mensaje.fecha not in mensajes_por_fecha:
            mensajes_por_fecha[mensaje.fecha] = []
        mensajes_por_fecha[mensaje.fecha].append(mensaje)
    
    for fecha, mensajes in mensajes_por_fecha.items():
        respuesta = ET.SubElement(salidaXml, "respuesta")
        
        #* Agregar la fecha
        fecha_element = ET.SubElement(respuesta, "fecha")
        fecha_element.text = fecha
        
        #* Agregar los mensajes totales
        mensajes_element = ET.SubElement(respuesta, "mensajes")
        total = ET.SubElement(mensajes_element, "total")
        total.text = str(len(mensajes))
        
        positivos = ET.SubElement(mensajes_element, "positivos")
        positivos.text = str(len([m for m in mensajes if m in mensajesPositivos]))
        
        negativos = ET.SubElement(mensajes_element, "negativos")
        negativos.text = str(len([m for m in mensajes if m in mensajesNegativos]))
        
        neutros = ET.SubElement(mensajes_element, "neutros")
        neutros.text = str(len([m for m in mensajes if m in mensajesNeutros]))
        
        # Agregar el análisis por empresa y servicio
        analisis = ET.SubElement(respuesta, "analisis")
        
        for empresa in empresasGlobal:
            empresa_element = ET.SubElement(analisis, "empresa", nombre=empresa.nombre)
            
            empresa_mensajes = ET.SubElement(empresa_element, "mensajes")
            empresa_total = ET.SubElement(empresa_mensajes, "total")
            empresa_total.text = str(len([m for m in mensajes if m in empresa.mensajes]))
            
            empresa_positivos = ET.SubElement(empresa_mensajes, "positivos")
            empresa_positivos.text = str(len([m for m in mensajes if m in empresa.mensajes and m in mensajesPositivos]))
            
            empresa_negativos = ET.SubElement(empresa_mensajes, "negativos")
            empresa_negativos.text = str(len([m for m in mensajes if m in empresa.mensajes and m in mensajesNegativos]))
            
            empresa_neutros = ET.SubElement(empresa_mensajes, "neutros")
            empresa_neutros.text = str(len([m for m in mensajes if m in empresa.mensajes and m in mensajesNeutros]))
            
            servicios_element = ET.SubElement(empresa_element, "servicios")
            
            for servicio in empresa.servicios:
                servicio_element = ET.SubElement(servicios_element, "servicio", nombre=servicio.nombre)
                
                servicio_mensajes = ET.SubElement(servicio_element, "mensajes")
                servicio_total = ET.SubElement(servicio_mensajes, "total")
                servicio_total.text = str(len([m for m in mensajes if m in servicio.mensajes]))
                
                servicio_positivos = ET.SubElement(servicio_mensajes, "positivos")
                servicio_positivos.text = str(len([m for m in mensajes if m in servicio.mensajes and m in mensajesPositivos]))
                
                servicio_negativos = ET.SubElement(servicio_mensajes, "negativos")
                servicio_negativos.text = str(len([m for m in mensajes if m in servicio.mensajes and m in mensajesNegativos]))
                
                servicio_neutros = ET.SubElement(servicio_mensajes, "neutros")
                servicio_neutros.text = str(len([m for m in mensajes if m in servicio.mensajes and m in mensajesNeutros]))
    
    # Convertir el árbol XML a una cadena con indentación
    rough_string = ET.tostring(salidaXml, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml_as_string = reparsed.toprettyxml(indent="  ")
    
    output_path = "C:\\Users\\josue\\Documents\\IPC2\\IPC2_Proyecto3_202247844\\backend\\salida.xml"
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(pretty_xml_as_string)
    
    return pretty_xml_as_string