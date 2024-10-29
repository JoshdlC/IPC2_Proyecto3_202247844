from . import views
from django.urls import path

urlpatterns = [
	path("indice", views.index, name="index"),
 	path("", views.home, name="home"),
	path("ayuda", views.ayuda, name="ayuda"),
 	path("peticiones", views.peticiones, name="peticiones"),
	path("cargarXml", views.cargarXml, name="cargarXml"),
	path("obtenerXmlSalida", views.obtenerXmlSalida, name="obtenerXmlSalida"),
]