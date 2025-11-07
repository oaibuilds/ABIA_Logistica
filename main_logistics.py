# main_logistics.py
from Gasolineras import Gasolineras
from CentrosDistribucion import CentrosDistribucion
from Camion import Camion
from SolucionBase import SolucionBase
from EstadoExtendido import EstadoExtendido
from LogisticaProblem import LogisticaProblem
from problem_parametres import ProblemParameters

from aima.search import hill_climbing

def construir_estado_inicial(params: ProblemParameters):
    gas = Gasolineras(num_gasolineras=params.gasolineras, seed=params.semilla)
    centers = CentrosDistribucion(num_centros=params.centros, multiplicidad=params.multiplicidad, seed=params.semilla)
    camiones = [Camion(camion_id=i, k=0, viajes=[]) for i in range(len(centers.centros))]

    # Solución inicial greedy
    estado = EstadoExtendido(gas, centers, camiones)
    SolucionBase(estado).build()
    return estado


def imprimir_estado(est):
    print("\n=== ESTADO ===")
    for c in est.camiones:
        print(f"Camión {c.id} | km={c.kilometraje} | viajes={len(c.ruta)}")
        for i, v in enumerate(c.ruta):
            print(f"  Viaje {i}: {v}")
    print(f"Heurística (beneficio estimado): {est.heuristic():.2f}")


def main():
    params = ProblemParameters(gasolineras=100,centros=10,semilla=1234,mul=1)
    estado_inicial = construir_estado_inicial(params)
    imprimir_estado(estado_inicial)

    problem = LogisticaProblem(estado_inicial)

    # === 1. Hill Climbing ===
    print("\n===== HILL CLIMBING =====")
    sol_hc = hill_climbing(problem)
    imprimir_estado(sol_hc)

if __name__ == "__main__":
    main()
