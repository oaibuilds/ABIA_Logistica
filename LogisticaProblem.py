from typing import Generator
from aima.search import Problem
from problem_operadors import ProblemOperator
from EstadoExtendido import EstadoExtendido


class LogisticaProblem(Problem):
    def __init__(self, initial_state: EstadoExtendido):
        super().__init__(initial_state)

    def actions(self, state: EstadoExtendido) -> Generator[ProblemOperator, None, None]:
        return state.generate_actions()

    def result(self, state: EstadoExtendido, action: ProblemOperator) -> EstadoExtendido:
        new_state = state.apply_action(action)
        # ⬇️ CLAVE: si la acción no es factible y devuelve None, nos quedamos en el mismo estado
        return new_state if new_state is not None else state

    def value(self, state: EstadoExtendido) -> float:
        # AIMA maximiza 'value'. Si tu heurística es 'menos es mejor',
        # usa el negativo. Protegemos por si llega un estado raro.
        h = getattr(state, "heuristic", lambda: float("inf"))()
        return -h

    def goal_test(self, state: EstadoExtendido) -> bool:
        # Sin condición de objetivo explícita; usar el mejor valor alcanzado.
        return False
