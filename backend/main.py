from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET

import requests

app = Flask(__name__)
xml_dataEntrada = None
xml_dataSalida = None

@app.route('/procesar_xml', methods=['POST'])
def procesar_xml():
    if 'archivo_xml' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo XML'}), 400

    archivo_xml = request.files['archivo_xml']
    tree = ET.parse(archivo_xml)
    root = tree.getroot()
    xml_content = ET.tostring(root, encoding='unicode')

    return jsonify({'xml_content': xml_content})


if __name__ == '__main__':
    app.run(debug=True)