# Camion.py
from typing import List, Tuple

class Camion:
    """
    Representa un camión con:
      - kilometraje usado (K1)
      - lista de viajes (R1): cada viaje es una lista de paradas (gid,pidx)
    Ejemplo:
        ruta = [
            [(0,0)],              # viaje 1
            [(3,1),(2,0)]         # viaje 2
        ]
    """

    def __init__(self, camion_id: int, k: int = 0, viajes: List[List[Tuple[int,int]]] = None):
        self.id = camion_id
        self.kilometraje = k
        self.ruta = viajes if viajes is not None else []  # lista de viajes
    
    def copy(self):
        # clona km y lista de viajes [(gid,pidx)] por viaje
        return Camion(self.id, self.kilometraje, [list(v) for v in self.ruta])

    # Validación estructural mínima (NO económica)
    def es_valido(self) -> bool:
        if len(self.ruta) > 5:
            return False
        for viaje in self.ruta:
            if len(viaje) > 2:
                return False
        if self.kilometraje > 640:
            return False
        return True

    def __repr__(self):
        return f"Camion {self.id} | viajes={len(self.ruta)} | km={self.kilometraje}"
