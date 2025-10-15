# === 1) Contexto fijo (envuelve tus listas y prepara distancias) ===
from dataclasses import dataclass
from typing import List, Tuple, Optional

from CentrosDistribucion import CentrosDistribucion
from Gasolineras import Gasolineras


@dataclass
class ProblemContext:
    gas: "Gasolineras"                 # tu objeto Gasolineras
    centers: "CentrosDistribucion"     # tu objeto CentrosDistribucion

    # derivadas sencillas para acceso rápido
    station_xy: List[Tuple[int,int]] = None
    center_xy: List[Tuple[int,int]] = None

    def __post_init__(self):
        # Coordenadas de gasolineras (cx, cy)
        self.station_xy = [(g.cx, g.cy) for g in self.gas.gasolineras]
        # Un centro por “camión” (multiplicidad => varias entradas)
        self.center_xy  = [(c.cx, c.cy) for c in self.centers.centros]

    @staticmethod
    def manhattan(a: Tuple[int,int], b: Tuple[int,int]) -> int:
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def petition_value_today(self, gid: int, pidx: int) -> int:
        """
        Define la fórmula de valor a partir de 'días pendientes'.
        Ajusta a lo que pida tu enunciado. Por ejemplo:
        """
        days = self.gas.gasolineras[gid].peticiones[pidx]  # 0 = hoy
        # Ejemplo simple: 1000 - 20*días (no estricta: cámbiala a tu fórmula real)
        return max(0, 1000 - 20*days)
