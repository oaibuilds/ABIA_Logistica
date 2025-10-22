from typing import List

class Camion(object):
    """
    Camion y su recorrido
    """

    def __init__(self, k: int, ruta: List, id = int):
        self.kilometraje = k
        self.ruta = ruta
        self.id = id

    def comprobark(self):
        return self.kilometraje <= 0
    
    def comprobarruta(self):
        return len(self.ruta) > 10
    
    def getid(self):
        return self.id
    
    def getk(self):
        return self.kilometraje
    
    def getr(self):
        return self.ruta
    
    def __repr__(self) -> str:
        return f"Camion numero {self.id}"   
    
    
    