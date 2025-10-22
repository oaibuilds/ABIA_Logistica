from Camion import Camion

class ProblemOperator(object):
    pass


class AñadirPeticion(ProblemOperator):
    def __init__(self, peticio1: int, centro_Dist: Camion):
        self.p1 = peticio1
        self.c = centro_Dist

    def __repr__(self) -> str:
        return f"Añadir {self.p1} a {self.c}"    

class QuitarPeticion(ProblemOperator):
    def __init__(self, peticio1: int, centro_Dist: Camion):
        self.p1 = peticio1
        self.c = centro_Dist

    def __repr__(self) -> str:
        return f"Quitar {self.p1} de {self.c}"      

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
    
class FusionarRutas(ProblemOperator):
    def __init__(self, centro_Dist1: Camion, centro_Dist2: Camion):
        self.c1 = centro_Dist1
        self.c2 = centro_Dist2

    def __repr__(self) -> str:
       return f"Fusionar {self.c1} y {self.c2}"  
    
class MoverPeticion(ProblemOperator):
    def __init__(self, peticio1: int, centro_Dist1: Camion, centro_Dist2: Camion):
        self.p1 = peticio1
        self.c1 = centro_Dist1
        self.c2 = centro_Dist2

    def __repr__(self) -> str:
       return f"Mover {self.p1} de {self.c1} a {self.c2}"  

class IntercambiarRuta(ProblemOperator):
    def __init__(self, centro_Dist1: Camion, centro_Dist2: Camion):
        self.c1 = centro_Dist1
        self.c2 = centro_Dist2

    def __repr__(self) -> str:
       return f"Intercambiar rutas entre {self.c1} y {self.c2}"  