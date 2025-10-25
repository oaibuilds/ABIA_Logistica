# Solucion.py

class Solution:
    """
    Superclase minimalista para representar una solución.
    - Guarda un Estado
    - Obliga a implementar build() en subclases
    - No calcula métricas, no almacena estructuras auxiliares
    """

    def __init__(self, estado):
        self.est = estado  # referencia al Estado

    @staticmethod
    def manhattan(a, b):
        """
        Calcula distancia Manhattan entre coordenadas 2D
        a = (x1,y1), b=(x2,y2)
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def build(self):
        """Debe ser implementado en subclases: construye/modifica self.est"""
        raise NotImplementedError

    def __repr__(self):
        # Representación delegada al Estado (no calculamos nada aquí)
        return repr(self.est)
