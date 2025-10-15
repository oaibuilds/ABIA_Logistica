from typing import List

DISTRIBUCION_PETICIONES = [0.05, 0.65, 0.25, 0.05]
DISTRIBUCION_DIAS = [0.60, 0.20, 0.15, 0.05]

class Gasolinera(object):
    """
    Estructura de datos de una gasolinera
    """

    def __init__(self, cx: int, cy: int, peticiones: List[int]):
        """
        Constructora
        :param cx: coordenada X
        :param cy: coordenada Y
        :param peticiones: ArrayList de Integers con los días pendientes de la peticion (0= hoy)
        """
        self.cx = cx
        self.cy = cy
        self.peticiones = peticiones
