# main_logistics.py
from Gasolineras import Gasolineras
from CentrosDistribucion import CentrosDistribucion
from Camion import Camion
from SolucionBase import SolucionBase
from EstadoExtendido import EstadoExtendido
from LogisticaProblem import LogisticaProblem
from problem_parametres import ProblemParameters
from aima.search import hill_climbing
import time


def construir_estado_inicial(params: ProblemParameters):
    gas = Gasolineras(num_gasolineras=params.gasolineras, seed=params.semilla)
    centers = CentrosDistribucion(num_centros=params.centros, multiplicidad=params.multiplicidad, seed=params.semilla)
    camiones = [Camion(camion_id=i, k=0, viajes=[]) for i in range(len(centers.centros))]

    # Solución inicial greedy
    estado = EstadoExtendido(gas, centers, camiones)
    SolucionBase(estado).build()
    return estado


def contar_peticiones(est: EstadoExtendido):
    """Devuelve (total, atendidas)"""
    total = sum(len(g.peticiones) for g in est.gasolineras.gasolineras)
    atendidas = 0
    for c in est.camiones:
        for viaje in c.ruta:
            atendidas += len(viaje)
    return total, atendidas


def imprimir_estado(est: EstadoExtendido):
    total, atendidas = contar_peticiones(est)

    print("\n=== ESTADO ===")
    for c in est.camiones:
        print(f"Camión {c.id} | km={c.kilometraje} | viajes={len(c.ruta)}")
        for i, v in enumerate(c.ruta):
            print(f"  Viaje {i}: {v}")
    print(f"\nPeticiones atendidas: {atendidas}/{total} ({100*atendidas/total:.1f}%)")
    print(f"Heurística (beneficio estimado): {est.heuristic():.2f}")


def main():
    params = ProblemParameters(gasolineras=100, centros=10, semilla=1234, mul=1)

    # === Medir tiempo de construcción de la solución inicial ===
    t0 = time.time()
    estado_inicial = construir_estado_inicial(params)
    t1 = time.time()
    segundos = (t1 - t0) * 1000

    imprimir_estado(estado_inicial)
    print(f"\nTiempo de construcción de la solución inicial: {segundos:.3f} milisegundos")
    problem = LogisticaProblem(estado_inicial)

    # === 1. Hill Climbing ===
    print("\n===== HILL CLIMBING =====")
    t0 = time.time()
    sol_hc = hill_climbing(problem)
    t1 = time.time()

    imprimir_estado(sol_hc)
    segundos = (t1 - t0) * 1000

    print(f"\nTiempo de ejecución del Hill Climbing: {segundos:.0f} milisegundos")



if __name__ == "__main__":
    main()
