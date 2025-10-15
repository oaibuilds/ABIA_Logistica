# estado.py
from dataclasses import dataclass
from typing import List, Tuple, Optional

# --- 0) Helpers de beneficio y distancia (según enunciado) ---
def valor_peticion(dias: int) -> int:
    # %precio = (100 - 2*dias) %, depósito vale 1000
    # Beneficio = 1000 * (100 - 2*dias) / 100
    return max(0, (100 - 2*dias) * 10)  # entero, p.ej. días=0 -> 1000; días=3 -> 940, etc.
# Fuente de la fórmula y criterios: enunciado. :contentReference[oaicite:2]{index=2} :contentReference[oaicite:3]{index=3}

def manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])  # d(D,G) = |Dx-Gx| + |Dy-Gy|. :contentReference[oaicite:4]{index=4}

# --- 1) Viaje (máximo 2 peticiones) ---
@dataclass
class Viaje:
    truck: int                       # id del camión (índice en centros.centros)
    items: List[Tuple[int,int]]      # [(id_gasolinera, idx_peticion_local)], len=1 ó 2
    km: int = 0
    valor: int = 0

# --- 2) Estado del día ---
class Estado:
    COSTE_POR_KM = 2                 # coste fijo por km. :contentReference[oaicite:5]{index=5}
    MAX_KM = 640                     # 80 km/h * 8 h. :contentReference[oaicite:6]{index=6}
    MAX_VIAJES = 5                   # límite de viajes/día. :contentReference[oaicite:7]{index=7}

    def __init__(self, gasolineras, centros):
        self.gas = gasolineras
        self.centros = centros
        self.trips_per_truck: List[List[Viaje]] = [[] for _ in self.centros.centros]
        self.km_used: List[int] = [0 for _ in self.centros.centros]
        self.total_km: int = 0
        self.total_valor: int = 0
        self.served: set[Tuple[int,int]] = set()  # (gid, pidx) ya servidas

    # --- recomputar km/valor de un viaje con el mejor orden si hay 2 paradas ---
    def recompute_viaje(self, v: Viaje):
        cx, cy = self._xy_centro(v.truck)
        if len(v.items) == 1:
            gid, pidx = v.items[0]
            gx, gy = self._xy_gas(gid)
            v.km = 2 * manhattan((cx, cy), (gx, gy))
            v.valor = valor_peticion(self.gas.gasolineras[gid].peticiones[pidx])
            return
        (g1,i1), (g2,i2) = v.items
        x1,y1 = self._xy_gas(g1); x2,y2 = self._xy_gas(g2)
        a = manhattan((cx,cy),(x1,y1)) + manhattan((x1,y1),(x2,y2)) + manhattan((x2,y2),(cx,cy))
        b = manhattan((cx,cy),(x2,y2)) + manhattan((x2,y2),(x1,y1)) + manhattan((x1,y1),(cx,cy))
        v.km = a if a < b else b
        v.valor = (
            valor_peticion(self.gas.gasolineras[g1].peticiones[i1]) +
            valor_peticion(self.gas.gasolineras[g2].peticiones[i2])
        )

    # --- constructores de viajes, respetando límites por camión ---
    def add_single(self, truck: int, gid: int, pidx: int) -> bool:
        if (gid, pidx) in self.served: return False
        if len(self.trips_per_truck[truck]) >= self.MAX_VIAJES: return False
        v = Viaje(truck=truck, items=[(gid, pidx)])
        self.recompute_viaje(v)
        if self.km_used[truck] + v.km > self.MAX_KM: return False
        self.trips_per_truck[truck].append(v)
        self.km_used[truck] += v.km
        self.total_km += v.km
        self.total_valor += v.valor
        self.served.add((gid, pidx))
        return True

    def pair_into(self, truck: int, trip_idx: int, gid: int, pidx: int) -> bool:
        if (gid, pidx) in self.served: return False
        trip = self.trips_per_truck[truck][trip_idx]
        if len(trip.items) != 1: return False
        km_old, val_old = trip.km, trip.valor
        trip.items.append((gid, pidx))
        self.recompute_viaje(trip)
        delta_km, delta_val = trip.km - km_old, trip.valor - val_old
        if self.km_used[truck] + delta_km > self.MAX_KM:
            trip.items.pop(); trip.km, trip.valor = km_old, val_old
            return False
        self.km_used[truck] += delta_km
        self.total_km += delta_km
        self.total_valor += delta_val
        self.served.add((gid, pidx))
        return True

    def objetivo(self) -> int:
        # Beneficio - 2 * km (criterio del enunciado). :contentReference[oaicite:8]{index=8}
        return self.total_valor - self.COSTE_POR_KM * self.total_km

    # --- utilidades privadas ---
    def _xy_centro(self, truck: int) -> Tuple[int,int]:
        c = self.centros.centros[truck]
        return (c.cx, c.cy)

    def _xy_gas(self, gid: int) -> Tuple[int,int]:
        g = self.gas.gasolineras[gid]
        return (g.cx, g.cy)
