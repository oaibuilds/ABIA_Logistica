# Solucion.py
from Solucion import Solution

class SolucionGreedy(Solution):
    """
    Llena camión a camión:
      - Previamente, ordena las peticiones por beneficio 
      - Para cada camión, recorre la lista de peticiones pendientes y va añadiendo
        mientras no viole: ≤5 viajes, ≤2 paradas/viaje, km ≤ 640.
      - Cuando ya no cabe más en ese camión, pasa al siguiente.
    Representación R1: camion.ruta = [ [ (gid,pidx) ], [ (gid,pidx),(gid,pidx) ], ... ]
    Modelo A (km): centro -> paradas -> centro (distancia Manhattan).
    """

    MAX_VIAJES = 5
    MAX_PARADAS = 2
    MAX_KM = 640
class SolucionGreedy(Solution):
    MAX_VIAJES = 5
    MAX_PARADAS = 2
    MAX_KM = 640

    def build(self):
        gas = self.est.gasolineras.gasolineras
        centers = self.est.centros.centros
        cams = self.est.camiones

        
        pendientes = [
            (gid, pidx)
            for gid, g in enumerate(gas)
            for pidx, _ in enumerate(getattr(g, "peticiones", []))
        ]

        # Ordenamos
        def beneficio_peticion(gid, pidx):
            dias = gas[gid].peticiones[pidx]
            return 1000 * (100 - 2 * dias) / 100.0  # segons enunciat

   
        pendientes.sort(
            key=lambda x: (
                beneficio_peticion(x[0], x[1]),  #Prioridad principal por beneficio 
                -gas[x[0]].peticiones[x[1]]      # Tambien damos prioridad por mas dias de espera
            ),
            reverse=True
        )
    

    
        for cam in cams:
            if not isinstance(cam.ruta, list):
                cam.ruta = []
            if not hasattr(cam, "kilometraje"):
                cam.kilometraje = 0


        for t, cam in enumerate(cams):
            hubo_asignacion = True
            while pendientes and hubo_asignacion:
                hubo_asignacion = False
                j = 0
                while j < len(pendientes):
                    pet = pendientes[j]
                    inc = self._km_inc_si_añado(cam, t, centers, pet)
                    if self._cabe(cam, inc):
                        self._asignar(cam, inc, pet)
                        pendientes.pop(j)
                        hubo_asignacion = True
                    else:
                        j += 1
        return self.est





    def _centro_xy(self, truck_idx, centers):
        c = centers[truck_idx]           
        return (c.cx, c.cy)

    def _gas_xy(self, gid):
        g = self.est.gasolineras.gasolineras[gid]
        return (g.cx, g.cy)

    def _km_viaje(self, c_xy, paradas):
        if len(paradas) == 1:
            p1 = self._gas_xy(paradas[0][0])
            return 2 * self.manhattan(c_xy, p1)
        p1 = self._gas_xy(paradas[0][0])
        p2 = self._gas_xy(paradas[1][0])
        return ( self.manhattan(c_xy, p1)
               + self.manhattan(p1, p2)
               + self.manhattan(p2, c_xy) )

    def _km_inc_si_añado(self, cam, truck_idx, centers, nueva):
        cxy = self._centro_xy(truck_idx, centers)
        if not cam.ruta:                          
            return self._km_viaje(cxy, [nueva])
        last = cam.ruta[-1]
        if len(last) == 1:                          
            return self._km_viaje(cxy, [last[0], nueva]) - self._km_viaje(cxy, last)
        return self._km_viaje(cxy, [nueva])

    def _cabe(self, cam, inc):
        abrir_nuevo = (not cam.ruta) or (len(cam.ruta[-1]) == self.MAX_PARADAS)
        if abrir_nuevo and len(cam.ruta) >= self.MAX_VIAJES:
            return False
        return (cam.kilometraje + inc) <= self.MAX_KM/2

    def _asignar(self, cam, inc, nueva):
        if not cam.ruta or len(cam.ruta[-1]) == self.MAX_PARADAS:
            cam.ruta.append([nueva])      
        else:
            cam.ruta[-1].append(nueva)     
        cam.kilometraje += inc

       
