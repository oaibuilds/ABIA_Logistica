import random
from Distribucion import Distribucion


class CentrosDistribucion(object):
    """
    Lista con los centros de distribución
    """

    def __init__(self, num_centros: int, multiplicidad: int, seed: int):
        """
        Genera un número de centros con una semilla aleatoria
        Si multiplicidad es diferente de 1 genera varios centros
        en la misma posicion para simular tener más de un camion
        en un centro
        :param num_centros: Número de centros
        :param multiplicidad: Multiplicidad en la misma posicion
        :param seed: Semilla para el generador de números aleatorios
        """
        self.centros = []
        self.my_random = random.Random(seed + 1)
        for _ in range(num_centros):
            centro = Distribucion(self.my_random.randint(0, 99),
                                  self.my_random.randint(0, 99))
            for _ in range(multiplicidad):
                self.centros.append(centro)