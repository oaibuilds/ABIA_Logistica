from Camion import Camion

class ProblemOperator(object):
    pass


# En problem_operadors.py

class AñadirPeticion(ProblemOperator):
    def __init__(self, peticio1, centro_Dist: Camion):
        # peticio1 es un Stop: (gid, pidx)
        self.p1 = peticio1
        self.c = centro_Dist

    def __repr__(self) -> str:
        gid, pidx = self.p1
        return f"AñadirPeticion(G={gid}, P={pidx}, C={self.c.id})"


class QuitarPeticion(ProblemOperator):
    def __init__(self, peticio1, centro_Dist: Camion):
        # peticio1 es un Stop: (gid, pidx)
        self.p1 = peticio1
        self.c = centro_Dist

    def __repr__(self) -> str:
        gid, pidx = self.p1
        return f"QuitarPeticion(G={gid}, P={pidx}, C={self.c.id})"

class MoverPeticion(ProblemOperator):
    def __init__(self, peticio1: int, centro_Dist1: Camion, centro_Dist2: Camion):
        self.p1 = peticio1
        self.c1 = centro_Dist1
        self.c2 = centro_Dist2

    def __repr__(self) -> str:
       return f"Mover {self.p1} de {self.c1} a {self.c2}"  

class ReinsertarEnMismoCamion(ProblemOperator):
    def __init__(self, peticio1, centro_Dist):
        self.p1 = peticio1  # (gid,pidx)
        self.c = centro_Dist
    def __repr__(self):
        gid, pidx = self.p1
        return f"ReinsertarEnMismoCamion(G={gid}, P={pidx}, C={getattr(self.c,'id','?')})"


class ReordenarPeticiones(ProblemOperator):
    def __init__(self, peticio1: int, peticio2: int, centro_Dist: Camion):
        self.p1 = peticio1
        self.p2 = peticio2
        self.c = centro_Dist

    def __repr__(self) -> str:
       return f"Intercambiar {self.p1} y {self.p2} en el camion {self.c}"  
    
class IntercambiarPeticiones(ProblemOperator):
    def __init__(self, peticio1: int, peticio2: int, centro_Dist1: Camion, centro_Dist2: Camion):
        self.p1 = peticio1
        self.p2 = peticio2
        self.c1 = centro_Dist1
        self.c2 = centro_Dist2

    def __repr__(self) -> str:
       return f"Intercambiar {self.p1} y {self.p2} entre {self.c1} y {self.c2}"  
    
class IntercambiarRuta(ProblemOperator):
    def __init__(self, centro_Dist1: Camion, centro_Dist2: Camion):
        self.c1 = centro_Dist1
        self.c2 = centro_Dist2

    def __repr__(self) -> str:
       return f"Intercambiar rutas entre {self.c1} y {self.c2}"  

class FusionarRutas(ProblemOperator):
    def __init__(self, centro_Dist1: Camion, centro_Dist2: Camion):
        self.c1 = centro_Dist1
        self.c2 = centro_Dist2

    def __repr__(self) -> str:
       return f"Fusionar {self.c1} y {self.c2}"  
    
class AtenderYDesatenderPeticion(ProblemOperator):
    def __init__(self, peticion1: int, peticion2: int):
        self.p1 = peticion1
        self.p2 = peticion2

    def __repr__(self) -> str:
       return f"Dejar de atender {self.p1} y atender {self.p2}"  



