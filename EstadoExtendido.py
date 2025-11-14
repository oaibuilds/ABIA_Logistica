# EstadoExtendido.py 
import copy
from typing import List, Tuple, Dict, Optional
from Estado import Estado
from Camion import Camion
from problem_operadors import (
    MoverPeticion, AñadirPeticion, QuitarPeticion, ReinsertarEnMismoCamion, AtenderYDesatenderPeticion
)

Stop = Tuple[int, int]  # (gid, pidx)


class EstadoExtendido(Estado):
    """
    Operadores disponibles:
      - MoverPeticion           (entre camiones, best-insertion en destino)
      - AñadirPeticion          (parada libre → camión, best-insertion)
      - QuitarPeticion          (eliminar parada asignada)
      - ReinsertarEnMismoCamion (reordenación interna con best-insertion)
      - AtenderYDesatenderPeticion (intercambia atendida por no atendida TOP-k)

    Mejoras clave:
      - 'operadores_activos' por estado (se propaga a copias)
      - Índice inverso de paradas (_pos_index)
      - Re-cálculo de km por camión afectado
    """

    MAX_VIAJES = 5
    MAX_PARADAS = 2
    MAX_KM = 640

    def __init__(self, gasolineras, centros, camiones):
        super().__init__(gasolineras, centros, camiones)
        # Set por defecto (equilibrio global-local): mover + add + remove
        self.operadores_activos = [
            "_posibles_movimientos",
            "_posibles_add",
            "_posibles_remove",
        ]
        # Índice inverso p -> (camion, viaje_idx, pos_idx)
        self._pos_index: Optional[Dict[Stop, Tuple[int, int, int]]] = None

    # ============ COPIA SEGURA E ÍNDICE ============

    def copy(self) -> "EstadoExtendido":
        gas_copy = self.gasolineras
        cen_copy = self.centros
        cam_copy: List[Camion] = [
            Camion(c.id, c.kilometraje, [list(v) for v in c.ruta]) for c in self.camiones
        ]
        new = EstadoExtendido(gas_copy, cen_copy, cam_copy)
        # Heredar set activo
        new.operadores_activos = list(getattr(self, "operadores_activos", []))
        # Reconstruir índice al vuelo cuando haga falta
        new._pos_index = None
        return new

    def _ensure_index(self):
        if not hasattr(self, "_pos_index") or self._pos_index is None:
            self._pos_index = self._build_index()

    def _build_index(self) -> Dict[Stop, Tuple[int, int, int]]:
        idx: Dict[Stop, Tuple[int, int, int]] = {}
        for cid, C in enumerate(self.camiones):
            for vidx, viaje in enumerate(C.ruta):
                for pidx, s in enumerate(viaje):
                    idx[s] = (cid, vidx, pidx)
        return idx

    def _clear_index_camion(self, cid: int):
        self._ensure_index()
        to_del = [s for s, loc in self._pos_index.items() if loc[0] == cid]
        for s in to_del:
            del self._pos_index[s]

    def _reindex_camion(self, cid: int):
        self._clear_index_camion(cid)
        C = self.camiones[cid]
        for vidx, viaje in enumerate(C.ruta):
            for pidx, s in enumerate(viaje):
                self._pos_index[s] = (cid, vidx, pidx)

    # ============ HELPERS ============

    def _stop_disponible(self, s: Stop) -> bool:
        self._ensure_index()
        return s not in self._pos_index

    def _paradas_disponibles(self):
        self._ensure_index()
        for gid, g in enumerate(self.gasolineras.gasolineras):
            for pidx, _dias in enumerate(g.peticiones):
                s = (gid, pidx)
                if s not in self._pos_index:
                    yield s

    # ============ GENERACIÓN DE ACCIONES POR SET ============

    def _destino_tiene_hueco(self, c_to: Camion) -> bool:
        if not c_to.ruta:
            return True
        if any(len(v) < self.MAX_PARADAS for v in c_to.ruta):
            return True
        return len(c_to.ruta) < self.MAX_VIAJES

    def _posibles_movimientos(self):
        for cf, camF in enumerate(self.camiones):
            for viaje in camF.ruta:
                for stop in viaje:
                    for ct, camT in enumerate(self.camiones):
                        if ct == cf:
                            continue
                        if self._destino_tiene_hueco(camT):
                            yield MoverPeticion(stop, self.camiones[cf], self.camiones[ct])

    def _posibles_add(self):
        for s in self._paradas_disponibles():
            for c in self.camiones:
                if self._destino_tiene_hueco(c):
                    yield AñadirPeticion(s, c)

    def _posibles_remove(self):
        for c in self.camiones:
            for v in c.ruta:
                for s in v:
                    yield QuitarPeticion(s, c)

    def _posibles_reinsert(self):
        for c in self.camiones:
            for v in c.ruta:
                for s in v:
                    yield ReinsertarEnMismoCamion(s, c)

    def _posibles_swap(self, k=3):
        # Intercambia una atendida por una no atendida entre las k mejores candidatas
        paradas_asignadas = []
        for c in self.camiones:
            for viaje in c.ruta:
                for s in viaje:
                    paradas_asignadas.append((s, c.id))
        paradas_libres = list(self._paradas_disponibles())
        paradas_libres.sort(key=lambda s: self._beneficio_estimado(s), reverse=True)
        top_candidates = paradas_libres[:k]
        for p1, _c_from in paradas_asignadas:
            for p2 in top_candidates:
                yield AtenderYDesatenderPeticion(p1, p2)

    def _beneficio_estimado(self, stop: Stop) -> float:
        gid, pidx = stop
        dias = self.gasolineras.gasolineras[gid].peticiones[pidx]
        return 1000.0 * factor_precio_por_dias(dias)

    def generate_actions(self):
        """Genera sucesores según la lista 'operadores_activos' (orden = prioridad)."""
        for op_name in getattr(self, "operadores_activos", []):
            gen = getattr(self, op_name, None)
            if callable(gen):
                yield from gen()

    # ============ KM / DISTANCIAS ============

    @staticmethod
    def _manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _centro_xy(self, truck_idx: int) -> Tuple[int, int]:
        c = self.centros.centros[truck_idx]
        return (c.cx, c.cy)

    def _gas_xy(self, gid: int) -> Tuple[int, int]:
        g = self.gasolineras.gasolineras[gid]
        return (g.cx, g.cy)

    def _km_viaje(self, c_xy: Tuple[int, int], paradas: List[Stop]) -> int:
        if len(paradas) == 0:
            return 0
        if len(paradas) == 1:
            p1 = self._gas_xy(paradas[0][0])
            return 2 * self._manhattan(c_xy, p1)
        p1 = self._gas_xy(paradas[0][0])
        p2 = self._gas_xy(paradas[1][0])
        return ( self._manhattan(c_xy, p1)
               + self._manhattan(p1, p2)
               + self._manhattan(p2, c_xy) )

    def _km_ruta(self, camion: Camion, truck_idx: int) -> int:
        c_xy = self._centro_xy(truck_idx)
        km = 0
        for viaje in camion.ruta:
            if viaje:
                km += self._km_viaje(c_xy, viaje)
        return km

    # ============ BEST-INSERTION ============

    def _delta_km_insercion(self, truck_idx: int, viaje: List[Stop], stop: Stop) -> tuple[int, List[Stop]]:
        c_xy = self._centro_xy(truck_idx)
        gid = stop[0]
        p_xy = self._gas_xy(gid)

        if len(viaje) == 0:
            km_new = 2 * self._manhattan(c_xy, p_xy)
            return km_new, [stop]

        if len(viaje) == 1:
            gid0 = viaje[0][0]
            p0_xy = self._gas_xy(gid0)
            km1 = ( self._manhattan(c_xy, p_xy)
                  + self._manhattan(p_xy, p0_xy)
                  + self._manhattan(p0_xy, c_xy) )
            km2 = ( self._manhattan(c_xy, p0_xy)
                  + self._manhattan(p0_xy, p_xy)
                  + self._manhattan(p_xy, c_xy) )
            km_old = 2 * self._manhattan(c_xy, p0_xy)
            if km1 - km_old <= km2 - km_old:
                return (km1 - km_old, [stop, viaje[0]])
            else:
                return (km2 - km_old, [viaje[0], stop])

        return (10**9, viaje)

    # ============ APLICACIÓN DE ACCIONES ============

    def apply_action(self, action):
        new = self.copy()
        new._ensure_index()

        if isinstance(action, MoverPeticion):
            p: Stop = action.p1
            c_from = action.c1.id
            c_to = action.c2.id
            removed = False
            for viaje in new.camiones[c_from].ruta:
                if p in viaje:
                    viaje.remove(p)
                    removed = True
                    break
            if not removed:
                return None
            new.camiones[c_from].ruta = [v for v in new.camiones[c_from].ruta if v]

            mejor_delta = 10**9
            mejor_plan: Optional[Tuple[str | int, List[Stop]]] = None

            if len(new.camiones[c_to].ruta) < self.MAX_VIAJES:
                c_xy = self._centro_xy(c_to)
                p_xy = self._gas_xy(p[0])
                delta_open = 2 * self._manhattan(c_xy, p_xy)
                mejor_delta = delta_open
                mejor_plan = ('nuevo', [p])

            for idx, v in enumerate(new.camiones[c_to].ruta):
                if len(v) < self.MAX_PARADAS:
                    delta, nuevo_viaje = self._delta_km_insercion(c_to, v, p)
                    if delta < mejor_delta:
                        mejor_delta = delta
                        mejor_plan = (idx, nuevo_viaje)

            if mejor_plan is None:
                return None

            if mejor_plan[0] == 'nuevo':
                new.camiones[c_to].ruta.append(mejor_plan[1])
            else:
                new.camiones[c_to].ruta[mejor_plan[0]] = mejor_plan[1]

            new.camiones[c_from].kilometraje = new._km_ruta(new.camiones[c_from], c_from)
            new.camiones[c_to].kilometraje = new._km_ruta(new.camiones[c_to], c_to)
            new._reindex_camion(c_from)
            new._reindex_camion(c_to)

        elif isinstance(action, AñadirPeticion):
            p: Stop = action.p1
            c_to = action.c.id
            if not new._stop_disponible(p):
                return None

            mejor_delta = 10**9
            mejor_plan: Optional[Tuple[str | int, List[Stop]]] = None

            if len(new.camiones[c_to].ruta) < self.MAX_VIAJES:
                c_xy = self._centro_xy(c_to)
                p_xy = self._gas_xy(p[0])
                delta_open = 2 * self._manhattan(c_xy, p_xy)
                mejor_delta = delta_open
                mejor_plan = ('nuevo', [p])

            for idx, v in enumerate(new.camiones[c_to].ruta):
                if len(v) < self.MAX_PARADAS:
                    delta, nuevo_viaje = self._delta_km_insercion(c_to, v, p)
                    if delta < mejor_delta:
                        mejor_delta = delta
                        mejor_plan = (idx, nuevo_viaje)

            if mejor_plan is None:
                return None

            if mejor_plan[0] == 'nuevo':
                new.camiones[c_to].ruta.append(mejor_plan[1])
            else:
                new.camiones[c_to].ruta[mejor_plan[0]] = mejor_plan[1]

            new.camiones[c_to].kilometraje = new._km_ruta(new.camiones[c_to], c_to)
            new._reindex_camion(c_to)

        elif isinstance(action, QuitarPeticion):
            p: Stop = action.p1
            c_from = action.c.id
            removed = False
            for viaje in new.camiones[c_from].ruta:
                if p in viaje:
                    viaje.remove(p)
                    removed = True
                    break
            if not removed:
                return None
            new.camiones[c_from].ruta = [v for v in new.camiones[c_from].ruta if v]
            new.camiones[c_from].kilometraje = new._km_ruta(new.camiones[c_from], c_from)
            new._reindex_camion(c_from)

        elif isinstance(action, ReinsertarEnMismoCamion):
            p = action.p1
            c_id = action.c.id

            # 1) quitar p de su viaje actual en c_id
            removed = False
            for v in new.camiones[c_id].ruta:
                if p in v:
                    v.remove(p)
                    removed = True
                    break
            if not removed:
                return None
            new.camiones[c_id].ruta = [v for v in new.camiones[c_id].ruta if v]

            # 2) best-insertion en el mismo camión
            mejor_delta = 10**9
            mejor_plan = None

            if len(new.camiones[c_id].ruta) < self.MAX_VIAJES:
                c_xy = self._centro_xy(c_id)
                p_xy = self._gas_xy(p[0])
                delta_open = 2 * self._manhattan(c_xy, p_xy)
                mejor_delta = delta_open
                mejor_plan = ('nuevo', [p])

            for idx, v in enumerate(new.camiones[c_id].ruta):
                if len(v) < self.MAX_PARADAS:
                    delta, nuevo_viaje = self._delta_km_insercion(c_id, v, p)
                    if delta < mejor_delta:
                        mejor_delta = delta
                        mejor_plan = (idx, nuevo_viaje)

            if mejor_plan is None:
                return None

            if mejor_plan[0] == 'nuevo':
                new.camiones[c_id].ruta.append(mejor_plan[1])
            else:
                new.camiones[c_id].ruta[mejor_plan[0]] = mejor_plan[1]

            # 3) actualizar km e índice
            new.camiones[c_id].kilometraje = new._km_ruta(new.camiones[c_id], c_id)
            new._reindex_camion(c_id)


        elif isinstance(action, AtenderYDesatenderPeticion):
            p1, p2 = action.p1, action.p2
            new._ensure_index()
            if p1 not in new._pos_index:
                return None
            c_from = new._pos_index[p1][0]

            # quitar p1
            for v in new.camiones[c_from].ruta:
                if p1 in v:
                    v.remove(p1)
                    break
            new.camiones[c_from].ruta = [v for v in new.camiones[c_from].ruta if v]

            # añadir p2 al primer camión con hueco
            added = False
            for c_to_id, cam in enumerate(new.camiones):
                if self._destino_tiene_hueco(cam):
                    if not cam.ruta:
                        cam.ruta.append([p2])
                    else:
                        for v in cam.ruta:
                            if len(v) < self.MAX_PARADAS:
                                v.append(p2)
                                break
                        else:
                            cam.ruta.append([p2])
                    added = True
                    cam.kilometraje = new._km_ruta(cam, c_to_id)
                    new._reindex_camion(c_to_id)
                    break
            if not added:
                return None

            new.camiones[c_from].kilometraje = new._km_ruta(new.camiones[c_from], c_from)
            new._reindex_camion(c_from)

        else:
            return None

        if not new._estado_valido(new):
            return None

        return new

    # ============ VALIDACIONES ============

    def _camion_valido(self, camion: Camion) -> bool:
        if len(camion.ruta) > self.MAX_VIAJES:
            return False
        for v in camion.ruta:
            if len(v) > self.MAX_PARADAS:
                return False
        if camion.kilometraje > self.MAX_KM:
            return False
        return True

    def _stops_unicos(self, est: "EstadoExtendido") -> bool:
        vistos = []
        for C in est.camiones:
            for v in C.ruta:
                vistos.extend(v)
        return len(vistos) == len(set(vistos))

    def _estado_valido(self, est: "EstadoExtendido") -> bool:
        for C in est.camiones:
            if not self._camion_valido(C):
                return False
        if not self._stops_unicos(est):
            return False
        return True

    # ============ HEURÍSTICA ============

    def heuristic(self) -> float:
        atendidas: set[Stop] = set()
        beneficio = 0.0

        for c in self.camiones:
            for viaje in c.ruta:
                for s in viaje:
                    atendidas.add(s)
                    gid, pidx = s
                    dias = self.gasolineras.gasolineras[gid].peticiones[pidx]
                    beneficio += 1000.0 * factor_precio_por_dias(dias)

        # penalización por diferir servicio (pérdida estimada)
        perdida = 0.0
        for gid, g in enumerate(self.gasolineras.gasolineras):
            for pidx, dias in enumerate(g.peticiones):
                s = (gid, pidx)
                if s not in atendidas:
                    factor_hoy = factor_precio_por_dias(dias)
                    factor_mana = factor_precio_por_dias(dias + 1)
                    perdida += 1000.0 * (factor_hoy - factor_mana)

        distancia_total = sum(c.kilometraje for c in self.camiones)
        self.ben = beneficio - 2.0 * float(distancia_total) - perdida

        # AIMA: minimizamos heuristic() → devolvemos coste
        return -(beneficio/5 - perdida - (2.0 * float(distancia_total)))


def factor_precio_por_dias(dias_espera: int) -> float:
    if dias_espera <= 0:
        return 1.02
    pct = (100.0 - pow(2.0, dias_espera)) / 100.0
    return max(0.0, min(pct, 1.02))

