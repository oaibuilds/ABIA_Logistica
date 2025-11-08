# EstadoExtendido.py (versión con mover + añadir best-insertion + quitar + reinsertar interno)
import copy
from typing import List, Tuple
from Estado import Estado
from Camion import Camion
from problem_operadors import MoverPeticion, AñadirPeticion, QuitarPeticion, ReinsertarEnMismoCamion, IntercambiarPeticiones

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
        gas_copy =  self.gasolineras  # escenario (con peticiones)
        cen_copy = self.centros                      # centros (inmutable en práctica)
        cam_copy: List[Camion] = []
        for c in self.camiones:
            new_c = Camion(
                camion_id=c.id,
                k=c.kilometraje,
                viajes=[list(v) for v in c.ruta]
            )
            cam_copy.append(new_c)
        return EstadoExtendido(gas_copy, cen_copy, cam_copy)

    # ============ HELPERS DE STOPS ============
    def _stops_asignados(self):
        asignados = set()
        for C in self.camiones:
            for v in C.ruta:
                for s in v:
                    asignados.add(s)
        return asignados

    def _stop_disponible(self, s: Stop, est: "EstadoExtendido" = None) -> bool:
        e = est or self
        for C in e.camiones:
            for v in C.ruta:
                if s in v:
                    return False
        return True

    def _paradas_disponibles(self):
        """Itera (gid,pidx) existentes en el escenario que aún no están asignadas a ningún camión."""
        asignados = self._stops_asignados()
        for gid, g in enumerate(self.gasolineras.gasolineras):
            for pidx, _dias in enumerate(g.peticiones):
                s = (gid, pidx)
                if s not in asignados:
                    yield s

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

    def _posibles_add(self):
        # Proponer añadir cualquier parada libre a cualquier camión con hueco
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
        # Reinsertar una parada dentro del mismo camión (cambio de viaje/posición)
        for c in self.camiones:
            for v in c.ruta:
                for s in v:
                    yield ReinsertarEnMismoCamion(s, c)
    
    def _destino_tiene_hueco(self, c_to: Camion) -> bool:
        """Filtro rápido para no proponer moves inviables."""
        if not c_to.ruta:
            return True  # puede abrir su primer viaje
        # ¿hay hueco en algún viaje existente?
        if any(len(v) < self.MAX_PARADAS for v in c_to.ruta):
            return True
        # si no, solo cabe si aún puede abrir un viaje nuevo
        return len(c_to.ruta) < self.MAX_VIAJES
    
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
        # Sin swaps: vecinos = mover entre camiones + añadir + quitar + reinsertar interno
        #yield from self._posibles_movimientos()
        #yield from self._posibles_swaps()
        yield from self._posibles_add()
        yield from self._posibles_remove()
        yield from self._posibles_reinsert()

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

    # ============ BEST-INSERTION ============
    def _delta_km_insercion(self, truck_idx: int, viaje: List[Stop], stop: Stop) -> tuple[int, List[Stop]]:
        """
        Devuelve (delta_km, nuevo_viaje) al insertar 'stop' en 'viaje' probando todas las posiciones válidas.
        Solo se usa cuando len(viaje) ∈ {0,1} (capacidad máxima 2).
        """
        c_xy = self._centro_xy(truck_idx)
        gid = stop[0]
        p_xy = self._gas_xy(gid)

        if len(viaje) == 0:
            # centro -> p -> centro
            km_old = 0
            km_new = 2 * self._manhattan(c_xy, p_xy)
            return km_new - km_old, [stop]

        if len(viaje) == 1:
            gid0 = viaje[0][0]
            p0_xy = self._gas_xy(gid0)

            # Opción 1: centro -> stop -> p0 -> centro
            km1 = ( self._manhattan(c_xy, p_xy)
                  + self._manhattan(p_xy, p0_xy)
                  + self._manhattan(p0_xy, c_xy) )

            # Opción 2: centro -> p0 -> stop -> centro
            km2 = ( self._manhattan(c_xy, p0_xy)
                  + self._manhattan(p0_xy, p_xy)
                  + self._manhattan(p_xy, c_xy) )

            km_old = 2 * self._manhattan(c_xy, p0_xy)

            if km1 <= km2:
                return (km1 - km_old, [stop, viaje[0]])
            else:
                return (km2 - km_old, [viaje[0], stop])

        # len == 2 no permitido (capacidad), devolver penalización
        return (10**9, viaje)

    # ============ APLICACIÓN DE ACCIONES + VALIDACIÓN ============
    def apply_action(self, action):
        new = self.copy()

        # ---- MOVER PETICIÓN (con best-insertion en destino) ----
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

            # 2) añadir a destino con BEST-INSERTION
            mejor_delta = 10**9
            mejor_plan = None  # ('nuevo', [p]) o (idx_viaje, nuevo_viaje)

            # opción abrir viaje nuevo si cabe
            if len(new.camiones[c_to].ruta) < self.MAX_VIAJES:
                c_xy = self._centro_xy(c_to)
                gid = p[0]
                p_xy = self._gas_xy(gid)
                delta_open = 2 * self._manhattan(c_xy, p_xy)  # km_old=0
                mejor_delta = delta_open
                mejor_plan = ('nuevo', [p])

            # opciones insertar en viajes existentes con hueco
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
                idx = mejor_plan[0]
                new.camiones[c_to].ruta[idx] = mejor_plan[1]

        # ---- AÑADIR PETICIÓN (best-insertion) ----
        elif isinstance(action, AñadirPeticion):
            p: Stop = action.p1
            c_to = action.c.id

            # la parada debe estar libre globalmente
            if not self._stop_disponible(p, new):
                return None

            mejor_delta = 10**9
            mejor_plan = None  # ('nuevo', [p]) o (idx_viaje, nuevo_viaje)

            # abrir viaje nuevo si cabe
            if len(new.camiones[c_to].ruta) < self.MAX_VIAJES:
                c_xy = self._centro_xy(c_to)
                gid = p[0]
                p_xy = self._gas_xy(gid)
                delta_open = 2 * self._manhattan(c_xy, p_xy)  # km_old=0
                mejor_delta = delta_open
                mejor_plan = ('nuevo', [p])

            # insertar en viajes existentes con hueco
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
                idx = mejor_plan[0]
                new.camiones[c_to].ruta[idx] = mejor_plan[1]

        # ---- QUITAR PETICIÓN ----
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

            # limpiar viajes vacíos
            new.camiones[c_from].ruta = [v for v in new.camiones[c_from].ruta if v]

        # ---- REINSERTAR EN MISMO CAMIÓN (reordenación interna) ----
        elif isinstance(action, ReinsertarEnMismoCamion):
            p: Stop = action.p1
            c_id = action.c.id

            # 1) quitar p del camión
            removed = False
            for viaje in new.camiones[c_id].ruta:
                if p in viaje:
                    viaje.remove(p)
                    removed = True
                    break
            if not removed:
                return None

            # 2) limpiar viajes vacíos
            new.camiones[c_id].ruta = [v for v in new.camiones[c_id].ruta if v]

            # 3) reinsertar p con best-insertion en el MISMO camión
            mejor_delta = 10**9
            mejor_plan = None

            # abrir viaje nuevo si cabe
            if len(new.camiones[c_id].ruta) < self.MAX_VIAJES:
                c_xy = self._centro_xy(c_id)
                gid = p[0]
                p_xy = self._gas_xy(gid)
                delta_open = 2 * self._manhattan(c_xy, p_xy)
                mejor_delta = delta_open
                mejor_plan = ('nuevo', [p])

            # insertar en viajes existentes
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
            return None  # operador no soportado

        # ---- Recalcular km y validar estado completo ----
        for t, C in enumerate(new.camiones):
            C.kilometraje = self._km_ruta(C, t)

        if not self._estado_valido(new):
            return None

        return new

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
        """Que no haya (gid,pidx) repetidos en ningún camión/viaje."""
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
        """
        Beneficio estimado =
            Σ(precio por petición atendida hoy)
            - Σ(pérdida esperada por peticiones no atendidas)
            - 2 * distancia_total

        El valor base de una petición es 1000.
        Las no atendidas pierden valor según el factor de precio por días.
        """
        # --- Copia ligera del estado (sin deepcopy estructural) ---
        gas_copy = [list(g.peticiones) for g in self.gasolineras.gasolineras]

        beneficio = 0.0

        # 1) Beneficio por peticiones atendidas
        for c in self.camiones:
            for viaje in c.ruta:
                for gid, pidx in viaje:
                    try:
                        dias = gas_copy[gid][pidx]
                        factor = factor_precio_por_dias(dias)
                        beneficio += 1000 * factor
                        # marcar como atendida (eliminar de la copia)
                        gas_copy[gid][pidx] = None
                    except Exception:
                        pass

        # 2) Pérdida por peticiones NO atendidas (valor hoy - valor mañana)
        perdida = 0.0
        for pet_list in gas_copy:
            for dias in pet_list:
                if dias is not None:
                    factor_hoy = factor_precio_por_dias(dias)
                    factor_mana = factor_precio_por_dias(dias + 1)
                    perdida += 1000 * (factor_hoy - factor_mana)

        # 3) Penalización por distancia recorrida
        distancia_total = sum(c.kilometraje for c in self.camiones)

        # 4) Resultado final
        beneficio -= perdida
        beneficio -= 2.0 * float(distancia_total)

        return beneficio


def factor_precio_por_dias(dias_espera: int) -> float:
    """
    Devuelve el factor multiplicador del precio según los días de espera.

    - Día 0 o antes: 102% del valor base.
    - A partir del día 1: (100 - 2^dias)%, acotado entre 0% y 102%.
    """
    if dias_espera <= 0:
        return 1.02  # 102% del precio base

    # Fórmula: 100 - 2^dias
    pct = (100.0 - pow(2.0, dias_espera)) / 100.0

    # Acotamos el resultado para evitar valores negativos o superiores a 1.02
    return max(0.0, min(pct, 1.02))
