from django.shortcuts import render

# Create your views here.
def viewName(request):
	context = {}
	return render(request, "nombre_de_app/home.html", context)