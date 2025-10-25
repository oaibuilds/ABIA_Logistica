# EstadoExtendido.py (versión revisada)
from typing import List, Tuple, Optional
from Estado import Estado
from Camion import Camion
from problem_operadors import MoverPeticion, IntercambiarPeticiones

Stop = Tuple[int, int]  # (gid, pidx)

class EstadoExtendido(Estado):
    """
    Extiende Estado con operadores y lógica de coste/validación
    compatible con problemas de búsqueda (AIMA, local search, etc.).
    - Representación de ruta (por camión): lista de viajes; cada viaje es lista de 'stops' (gid, pidx).
    - Distancia: Manhattan. Un viaje es centro -> p1 [-> p2] -> centro.
    - Restricciones por camión: ≤ 5 viajes, ≤ 2 paradas por viaje, km ≤ 640.
    """

    # --- PARÁMETROS DE RESTRICCIÓN ---
    MAX_VIAJES = 5
    MAX_PARADAS = 2
    MAX_KM = 640

    # ============ COPIA PROFUNDA SEGURA ============
    def copy(self) -> "EstadoExtendido":
        gas_copy = self.gasolineras
        cen_copy = self.centros
        cam_copy: List[Camion] = []
        for c in self.camiones:
            new_c = Camion(
                camion_id=c.id,
                k=c.kilometraje,
                viajes=[list(v) for v in c.ruta]
            )
            cam_copy.append(new_c)
        return EstadoExtendido(gas_copy, cen_copy, cam_copy)

    # ============ GENERACIÓN DE ACCIONES ============
    def _destino_tiene_hueco(self, c_to: Camion) -> bool:
        """Filtro rápido para no proponer moves inviables."""
        if not c_to.ruta:
            return True  # puede abrir su primer viaje
        # ¿hay hueco en algún viaje existente?
        if any(len(v) < self.MAX_PARADAS for v in c_to.ruta):
            return True
        # si no, solo cabe si aún puede abrir un viaje nuevo
        return len(c_to.ruta) < self.MAX_VIAJES

    def _posibles_movimientos(self):
        # Mover (gid,pidx) de un camión a otro (i != j)
        for cf, camF in enumerate(self.camiones):
            for viaje in camF.ruta:
                for stop in viaje:
                    for ct, camT in enumerate(self.camiones):
                        if ct == cf:
                            continue
                        if self._destino_tiene_hueco(camT):
                            yield MoverPeticion(stop, self.camiones[cf], self.camiones[ct])

    def _posibles_swaps(self):
        """
        Intercambiar paradas entre camiones Y también dentro del mismo camión.
        Permitir cb == ca y p1 != p2 habilita permutaciones completas internas.
        """
        for ca in range(len(self.camiones)):
            for cb in range(ca, len(self.camiones)):  # incluye intra-camión
                for va in self.camiones[ca].ruta:
                    for vb in self.camiones[cb].ruta:
                        for p1 in va:
                            for p2 in vb:
                                if (ca != cb) or (p1 != p2):
                                    yield IntercambiarPeticiones(p1, p2, self.camiones[ca], self.camiones[cb])

    def generate_actions(self):
        # Primero swaps (muy ricos), luego movimientos ya filtrados
        yield from self._posibles_swaps()
        yield from self._posibles_movimientos()

    # ============ APLICACIÓN DE ACCIONES + VALIDACIÓN ============
    def apply_action(self, action):
        new = self.copy()

        if isinstance(action, MoverPeticion):
            p: Stop = action.p1
            c_from = action.c1.id
            c_to = action.c2.id

            # 1) quitar de origen
            removed = False
            for viaje in new.camiones[c_from].ruta:
                if p in viaje:
                    viaje.remove(p)
                    removed = True
                    break
            if not removed:
                return None

            # limpia viajes vacíos
            new.camiones[c_from].ruta = [v for v in new.camiones[c_from].ruta if v]

            # 2) añadir a destino respetando capacidad
            if not new.camiones[c_to].ruta:
                new.camiones[c_to].ruta.append([p])
            else:
                # prioriza rellenar un viaje con < MAX_PARADAS
                colocado = False
                for v in new.camiones[c_to].ruta:
                    if len(v) < self.MAX_PARADAS:
                        v.append(p)
                        colocado = True
                        break
                if not colocado:
                    # abrir viaje nuevo si cabe
                    if len(new.camiones[c_to].ruta) < self.MAX_VIAJES:
                        new.camiones[c_to].ruta.append([p])
                    else:
                        return None  # no cabe

        elif isinstance(action, IntercambiarPeticiones):
            p1: Stop = action.p1
            p2: Stop = action.p2
            c1 = action.c1.id
            c2 = action.c2.id

            i1 = j1 = i2 = j2 = None
            for i, v in enumerate(new.camiones[c1].ruta):
                if p1 in v:
                    i1, j1 = i, v.index(p1)
                    break
            for i, v in enumerate(new.camiones[c2].ruta):
                if p2 in v:
                    i2, j2 = i, v.index(p2)
                    break

            if i1 is None or i2 is None:
                return None

            # swap directo
            new.camiones[c1].ruta[i1][j1], new.camiones[c2].ruta[i2][j2] = \
                new.camiones[c2].ruta[i2][j2], new.camiones[c1].ruta[i1][j1]

        else:
            return None

        # 3) Recalcular kilómetros de todos los camiones
        for t, C in enumerate(new.camiones):
            C.kilometraje = self._km_ruta(C, t)

        # 4) Validar restricciones + unicidad global de paradas
        if not self._estado_valido(new):
            return None

        return new

    # ============ DISTANCIAS / KM ============
    @staticmethod
    def _manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _centro_xy(self, truck_idx: int) -> Tuple[int, int]:
        c = self.centros.centros[truck_idx]  # centro t → centers[t]
        return (c.cx, c.cy)

    def _gas_xy(self, gid: int) -> Tuple[int, int]:
        g = self.gasolineras.gasolineras[gid]
        return (g.cx, g.cy)

    def _km_viaje(self, c_xy: Tuple[int, int], paradas: List[Stop]) -> int:
        """
        Un viaje:
          - 1 parada:  centro -> p1 -> centro
          - 2 paradas: centro -> p1 -> p2 -> centro
        """
        if len(paradas) == 0:
            return 0
        if len(paradas) == 1:
            p1 = self._gas_xy(paradas[0][0])
            return 2 * self._manhattan(c_xy, p1)
        # len == 2 (máximo)
        p1 = self._gas_xy(paradas[0][0])
        p2 = self._gas_xy(paradas[1][0])
        return ( self._manhattan(c_xy, p1)
               + self._manhattan(p1, p2)
               + self._manhattan(p2, c_xy) )

    def _km_ruta(self, camion: Camion, truck_idx: int) -> int:
        c_xy = self._centro_xy(truck_idx)
        km = 0
        for viaje in camion.ruta:
            if len(viaje) > 0:
                km += self._km_viaje(c_xy, viaje)
        return km

    # ============ VALIDACIONES ============
    def _camion_valido(self, camion: Camion) -> bool:
        # (1) límite de viajes
        if len(camion.ruta) > self.MAX_VIAJES:
            return False
        # (2) máximo 2 paradas por viaje
        for v in camion.ruta:
            if len(v) > self.MAX_PARADAS:
                return False
        # (3) km máximo
        if camion.kilometraje > self.MAX_KM:
            return False
        return True

    def _stops_unicos(self, est: "EstadoExtendido") -> bool:
        """Que no haya (gid,pidx) repetidos en ningún camión/viage."""
        vistos = []
        for C in est.camiones:
            for v in C.ruta:
                for s in v:
                    vistos.append(s)
        return len(vistos) == len(set(vistos))

    def _estado_valido(self, est: "EstadoExtendido") -> bool:
        # todos los camiones válidos
        for C in est.camiones:
            if not self._camion_valido(C):
                return False
        # unicidad global de paradas
        if not self._stops_unicos(est):
            return False
        return True

    # ============ HEURÍSTICA SIMPLE ============
    def heuristic(self) -> float:
        cam_usados = sum(1 for c in self.camiones if c.ruta)
        total_stops = sum(len(v) for c in self.camiones for v in c.ruta)
        # Heurística barata que favorece menos camiones y menos paradas
        return cam_usados + 0.01 * total_stops
