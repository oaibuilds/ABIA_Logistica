# Solucion.py
from Solucion import Solution

class SolucionBase(Solution):
    """
    Llena camión a camión:
      - Para cada camión, recorre la lista de peticiones pendientes y va añadiendo
        mientras no viole: ≤5 viajes, ≤2 paradas/viaje, km ≤ 640.
      - Cuando ya no cabe más en ese camión, pasa al siguiente.
    Representación R1: camion.ruta = [ [ (gid,pidx) ], [ (gid,pidx),(gid,pidx) ], ... ]
    Modelo A (km): centro -> paradas -> centro (distancia Manhattan).
    """

    MAX_VIAJES = 5
    MAX_PARADAS = 2
    MAX_KM = 640

    def build(self):
        gas = self.est.gasolineras.gasolineras
        centers = self.est.centros.centros
        cams = self.est.camiones

        # Lista de peticiones pendientes [(gid, pidx), ...]
        pendientes = [(gid, pidx)
                      for gid, g in enumerate(gas)
                      for pidx, _ in enumerate(getattr(g, "peticiones", []))]

        # Normaliza estructura mínima de camiones
        for cam in cams:
            if not isinstance(cam.ruta, list): cam.ruta = []
            if not hasattr(cam, "kilometraje"): cam.kilometraje = 0

        # Recorre camiones; a cada uno le intenta añadir tantas peticiones como quepan
        for t, cam in enumerate(cams):
            hubo_asignacion = True
            while pendientes and hubo_asignacion:
                hubo_asignacion = False
                j = 0
                # barrido simple por las pendientes: si cabe, asigna y elimina
                while j < len(pendientes):
                    pet = pendientes[j]
                    inc = self._km_inc_si_añado(cam, t, centers, pet)
                    if self._cabe(cam, inc):
                        self._asignar(cam, inc, pet)
                        pendientes.pop(j)
                        hubo_asignacion = True
                        # seguimos con j (no incrementa) para intentar seguir llenando
                    else:
                        j += 1
                # si en este barrido no cupo ninguna, pasamos al siguiente camión
        return self.est

    # =============== Helpers mínimos ===============

    def _centro_xy(self, truck_idx, centers):
        c = centers[truck_idx]           # C1: centro t → centers[t]
        return (c.cx, c.cy)

    def _gas_xy(self, gid):
        g = self.est.gasolineras.gasolineras[gid]
        return (g.cx, g.cy)

    def _km_viaje(self, c_xy, paradas):
        # 1 parada:  centro->p->centro  ; 2 paradas: centro->p1->p2->centro
        if len(paradas) == 1:
            p1 = self._gas_xy(paradas[0][0])
            return 2 * self.manhattan(c_xy, p1)
        p1 = self._gas_xy(paradas[0][0])
        p2 = self._gas_xy(paradas[1][0])
        return ( self.manhattan(c_xy, p1)
               + self.manhattan(p1, p2)
               + self.manhattan(p2, c_xy) )

    def _km_inc_si_añado(self, cam, truck_idx, centers, nueva):
        """Km incrementales por añadir 'nueva' al último viaje o abriendo uno nuevo."""
        cxy = self._centro_xy(truck_idx, centers)
        if not cam.ruta:                               # abrir 1º viaje
            return self._km_viaje(cxy, [nueva])
        last = cam.ruta[-1]
        if len(last) == 1:                             # completar 2ª parada
            return self._km_viaje(cxy, [last[0], nueva]) - self._km_viaje(cxy, last)
        # último ya con 2 paradas → abrir viaje nuevo
        return self._km_viaje(cxy, [nueva])

    def _cabe(self, cam, inc):
        """Chequea restricciones estructurales y km."""
        # si hay que abrir viaje nuevo y ya tiene 5 → no cabe
        abrir_nuevo = (not cam.ruta) or (len(cam.ruta[-1]) == self.MAX_PARADAS)
        if abrir_nuevo and len(cam.ruta) >= self.MAX_VIAJES:
            return False
        # km
        return (cam.kilometraje + inc) <= self.MAX_KM

    def _asignar(self, cam, inc, nueva):
        """Aplica la asignación (ya validada)."""
        if not cam.ruta or len(cam.ruta[-1]) == self.MAX_PARADAS:
            cam.ruta.append([nueva])       # viaje nuevo con 1 parada
        else:
            cam.ruta[-1].append(nueva)     # completar viaje actual a 2
        cam.kilometraje += inc
