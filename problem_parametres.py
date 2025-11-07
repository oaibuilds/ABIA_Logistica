from typing import List


class ProblemParameters(object):
    def __init__(self, gasolineras: int, centros: int, semilla: int, mul: int ):
        self.gasolineras = gasolineras  # Numero total de gasolineras
        self.centros = centros      # Numero total de centros
        self.semilla = semilla  # Semilla aleatorea
        self.multiplicidad = mul #multiplicidad

    def __repr__(self):
        return f"Params(Nº de gasolineras={self.gasolineras}, Nº de centros={self.centros}, Semilla={self.semilla}, Multiplicidad={self.multiplicidad})"