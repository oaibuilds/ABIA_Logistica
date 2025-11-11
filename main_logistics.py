# main_logistics.py
from Gasolineras import Gasolineras
from CentrosDistribucion import CentrosDistribucion
from Camion import Camion
from SolucionBase import SolucionBase
from SolucionGreedy import SolucionGreedy
from SolucionVacia import SolucionVacia
from EstadoExtendido import EstadoExtendido
from LogisticaProblem import LogisticaProblem
from problem_parametres import ProblemParameters
from aima.search import hill_climbing
import time
import random


def construir_estado_inicial(params: ProblemParameters):
    gas = Gasolineras(num_gasolineras=params.gasolineras, seed=params.semilla)
    centers = CentrosDistribucion(num_centros=params.centros, multiplicidad=params.multiplicidad, seed=params.semilla)
    camiones = [Camion(camion_id=i, k=0, viajes=[]) for i in range(len(centers.centros))]

    # Solución inicial greedy
    estado = EstadoExtendido(gas, centers, camiones)
    SolucionVacia(estado).build()
    return estado


def contar_peticiones(est: EstadoExtendido):
    """Devuelve (total, atendidas)"""
    total = sum(len(g.peticiones) for g in est.gasolineras.gasolineras)
    atendidas = 0
    for c in est.camiones:
        for viaje in c.ruta:
            atendidas += len(viaje)
    return total, atendidas


'''def imprimir_estado(est: EstadoExtendido):
    total, atendidas = contar_peticiones(est)

    print("\n=== ESTADO ===")
    for c in est.camiones:
        print(f"Camión {c.id} | km={c.kilometraje} | viajes={len(c.ruta)}")
        for i, v in enumerate(c.ruta):
            print(f"  Viaje {i}: {v}")
    print(f"\nPeticiones atendidas: {atendidas}/{total} ({100*atendidas/total:.1f}%)")
    print(f"Heurística (beneficio estimado): {est.heuristic():.2f}")'''


def medir_tiempo_y_beneficio(func, params, repeticiones=1, usar_estado_inicial=False):
    """
    Mide tiempo medio y beneficio medio de una función.
    Si usar_estado_inicial es True, se construye un estado inicial distinto para cada iteración.
    """
    tiempos = []
    beneficios = []

    for _ in range(repeticiones):
        # Cambiamos la semilla
        params.semilla = 1234

        # Construcción del estado inicial si es necesario
        if usar_estado_inicial:
            estado_inicial = construir_estado_inicial(params)
            arg = LogisticaProblem(estado_inicial)
        else:
            arg = params

        t0 = time.time()
        solucion = func(arg)
        t1 = time.time()

        tiempos.append(t1 - t0)

        # Calculamos beneficio
        if hasattr(solucion, 'beneficio'):
            beneficios.append(solucion.beneficio)
        elif hasattr(solucion, 'calcular_beneficio'):
            beneficios.append(solucion.calcular_beneficio())
        elif hasattr(solucion, 'heuristic'):
            beneficios.append(solucion.heuristic())

    tiempo_medio = sum(tiempos) / repeticiones * 1000
    beneficio_medio = sum(beneficios) / len(beneficios) if beneficios else None
    return solucion, tiempo_medio, beneficio_medio


def main():
    params = ProblemParameters(gasolineras=100, centros=10, semilla=2143, mul=1)

    # === Construcción de la solución inicial ===
    estado_inicial, tiempo_init, beneficio_init = medir_tiempo_y_beneficio(construir_estado_inicial, params)
    # imprimir_estado(estado_inicial)  # Comentado según petición
    print(f"\nTiempo medio de construcción de la solución inicial: {tiempo_init:.3f} ms")
    if beneficio_init is not None:
        print(f"Beneficio medio de la solución inicial: {beneficio_init:.2f}")
    if hasattr(estado_inicial, 'ben'):
        print(f"BENEFICIO DIARIO (inicial): {estado_inicial.ben:.2f}")

    # === Hill Climbing ===
    print("\n===== HILL CLIMBING =====")
    # Pasamos usar_estado_inicial=True para construir un estado distinto cada iteración
    sol_hc, tiempo_hc, beneficio_hc = medir_tiempo_y_beneficio(hill_climbing, params, usar_estado_inicial=True)
    # imprimir_estado(sol_hc)  # Comentado
    print(f"\nTiempo medio de ejecución del Hill Climbing: {tiempo_hc:.0f} ms")
    if beneficio_hc is not None:
        print(f"Beneficio medio del Hill Climbing: {beneficio_hc:.2f}")
    if hasattr(sol_hc, 'ben'):
        print(f"BENEFICIO DIARIO (Hill Climbing): {sol_hc.ben:.2f}")

if __name__ == "__main__":
    main()
