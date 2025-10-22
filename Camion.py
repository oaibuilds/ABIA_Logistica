from typing import List

class Camion(object):
    """
    Camion y su recorrido
    """

    def __init__(self, k: int, ruta: List):
        self.kilometraje = k
        self.ruta = ruta

    def comprobar(self,k):
        return k <= 0