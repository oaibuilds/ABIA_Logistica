from typing import Generator
from aima.search import Problem
from problem_operadors import ProblemOperator
from EstadoExtendido import EstadoExtendido
from Gasolineras import Gasolineras


class LogisticaProblem(Problem):
    def __init__(self, initial_state: EstadoExtendido):
        super().__init__(initial_state)

    def actions(self, state: EstadoExtendido) -> Generator[ProblemOperator, None, None]:
        return state.generate_actions()

    def result(self, state: EstadoExtendido, action: ProblemOperator) -> EstadoExtendido:
        new_state = state.apply_action(action)
        return new_state if new_state is not None else state

    def value(self, state: EstadoExtendido) -> float:
        h = getattr(state, "heuristic", lambda: float("inf"))()
        return -h

    def goal_test(self, state: EstadoExtendido) -> bool:
        return False
