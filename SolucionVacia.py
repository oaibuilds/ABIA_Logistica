# Solucion.py
from Solucion import Solution

class SolucionGreedy(Solution):
    """
    Llena camión a camión:
      - Para cada camión, recorre la lista de peticiones pendientes y va añadiendo
        mientras no viole: ≤5 viajes, ≤2 paradas/viaje, km ≤ 640.
      - Cuando ya no cabe más en ese camión, pasa al siguiente.
    Representación R1: camion.ruta = [ [ (gid,pidx) ], [ (gid,pidx),(gid,pidx) ], ... ]
    Modelo A (km): centro -> paradas -> centro (distancia Manhattan).
    """

    MAX_VIAJES = 5
    MAX_PARADAS = 2
    MAX_KM = 640
class SolucionVacia(Solution):

    def build(self):

        return self.est

       
