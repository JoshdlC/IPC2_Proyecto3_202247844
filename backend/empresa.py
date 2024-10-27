from mensaje import Mensaje

class Empresa:
    def __init__(self, nombre, servicios):
        self.nombre = nombre
        self.servicios = servicios
        self.mensajes = Mensaje()

    def agregar_servicio(self, servicio):
        self.servicios.append(servicio)

    def __str__(self):
        return f"Empresa: {self.nombre}, Servicios: {', '.join(self.servicios)}"
    
class Servicio:
    def __init__(self, nombre, alias):
        self.nombre = nombre
        self.alias = alias
        self.mensajes = Mensaje()

