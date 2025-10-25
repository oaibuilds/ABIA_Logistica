# estado_base.py
class Estado:
    """
    Solo define el estado:
      - gasolineras (escenario)
      - centros (escenario)
      - lista de camiones (cada uno con su km y ruta)
    No implementa operadores ni coste.
    """

    def __init__(self, gasolineras, centros, camiones):
        self.gasolineras = gasolineras
        self.centros = centros
        self.camiones = camiones 
        
    def copy(self):
        gas_copy = self.gasolineras   # escenario fijo
        cen_copy = self.centros       # escenario fijo
        cam_copy = [c.copy() for c in self.camiones]  # clona lista de camiones
        return Estado(gas_copy, cen_copy, cam_copy) 

    def __repr__(self):
        return f"<Estado camiones={len(self.camiones)}>"
