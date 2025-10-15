import random
from Gasolinera import Gasolinera
from typing import List, Tuple

from Gasolinera import DISTRIBUCION_DIAS, DISTRIBUCION_PETICIONES

class Gasolineras(object):
    """
    Lista de gasolineras
    """

    def __init__(self, num_gasolineras: int, seed: int):
        """
        Genera un número de centros con una semilla aleatoria
        :param num_gasolineras: Número de gasolineras
        :param seed: Semilla para el generador de números aleatorios
        """
        self.my_random = random.Random(seed)
        self.gasolineras = []
        for _ in range(num_gasolineras):
            gasolinera = Gasolinera(self.my_random.randint(0, 99),
                                    self.my_random.randint(0, 99),
                                    self.genera_peticiones())
            self.gasolineras.append(gasolinera)

    def genera_peticiones(self) -> List[int]:
        """
        Generamos un número de peticiones entre 0 y 3 con distribución sesgada
        Generamos el día que lleva la peticion pendiente con otra distribución
        sesgada
        :return: Lista de peticiones
        """
        pet = []
        dice = self.my_random.random()
        if dice < DISTRIBUCION_PETICIONES[0]:
            num_peticiones = 0
        elif dice < (DISTRIBUCION_PETICIONES[0] + DISTRIBUCION_PETICIONES[1]):
            num_peticiones = 1
        else:
            num_peticiones = 2

        for _ in range(num_peticiones):
            dice = self.my_random.random()
            if dice < DISTRIBUCION_DIAS[0]:
                num_dias = 0
            elif dice < (DISTRIBUCION_DIAS[0] + DISTRIBUCION_DIAS[1]):
                num_dias = 1
            elif dice < (DISTRIBUCION_DIAS[0] + DISTRIBUCION_DIAS[1] + DISTRIBUCION_DIAS[2]):
                num_dias = 2
            else:
                num_dias = 3
            pet.append(num_dias)
        return pet