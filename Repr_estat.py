from __future__ import annotations

from typing import List, Set, Generator

from problem_operadors import *
from problem_parametres import ProblemParameters
from Camion import Camion


class StateRepresentation(object):
    def __init__(self, params: ProblemParameters, rutes: List[Camion]):
        self.params = params
        self.rutes = rutes

    def copy(self) -> StateRepresentation:
        # Afegim el copy per cada set!
        rutes_copy = [set_i.copy() for set_i in self.rutes]
        return StateRepresentation(self.params, rutes_copy)
    
    def getruta(self,id):
        return self.rutes[id].getr()

    def __repr__(self) -> str:
        return f"{self.params, self.rutes}"