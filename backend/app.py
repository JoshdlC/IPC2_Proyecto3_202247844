from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET
import requests

app = Flask(__name__)

