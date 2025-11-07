import random
from Distribucion import Distribucion
from Gasolinera import *
from Gasolineras import *


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

if __name__ == "__main__":
    """
    Código para probar las clases
    No tiene utilidad para la práctica
    """
    s = Gasolineras(100, 1234)
    c = CentrosDistribucion(10, 1, 1234)
    histograma = [0, 0, 0, 0]

    for i in range(len(s.gasolineras)):
        print(f"Gasolinera {i}: {s.gasolineras[i].cx} {s.gasolineras[i].cy}")
        j = 0
        if not s.gasolineras[i].peticiones:
            print("-> Sin peticiones <-")
        for peticion in s.gasolineras[i].peticiones:
            print(f"Peticion {j}: Días {peticion}")
            j += 1
            histograma[peticion] += 1

    print()
    for i in range(4):
        print(f"{histograma[i]} de {i} días")
    print()
    for i in range(len(c.centros)):
        print(f"Centro {i}: {c.centros[i].cx} {c.centros[i].cy}")