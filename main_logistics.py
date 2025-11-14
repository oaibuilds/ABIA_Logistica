# main_logistics.py
from Gasolineras import Gasolineras
from CentrosDistribucion import CentrosDistribucion
from Camion import Camion
from SolucionBase import SolucionBase
from EstadoExtendido import EstadoExtendido
from LogisticaProblem import LogisticaProblem
from problem_parametres import ProblemParameters
from aima.search import hill_climbing, simulated_annealing, exp_schedule
import time


def construir_estado_inicial(params: ProblemParameters):
    gas = Gasolineras(num_gasolineras=params.gasolineras, seed=params.semilla)
    centers = CentrosDistribucion(num_centros=params.centros, multiplicidad=params.multiplicidad, seed=params.semilla)
    camiones = [Camion(camion_id=i, k=0, viajes=[]) for i in range(len(centers.centros))]

    estado = EstadoExtendido(gas, centers, camiones)
    SolucionBase(estado).build()
    return estado


def contar_peticiones(est: EstadoExtendido):
    total = sum(len(g.peticiones) for g in est.gasolineras.gasolineras)
    atendidas = 0
    for c in est.camiones:
        for viaje in c.ruta:
            atendidas += len(viaje)
    return total, atendidas


def medir_tiempo_y_beneficio(func, params, repeticiones=1, usar_estado_inicial=False):
    tiempos = []
    beneficios = []

    for _ in range(repeticiones):
        if usar_estado_inicial:
            estado_inicial = construir_estado_inicial(params)
            arg = LogisticaProblem(estado_inicial)
        else:
            arg = params

        t0 = time.time()
        solucion = func(arg)
        t1 = time.time()

        tiempos.append(t1 - t0)

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
    params = ProblemParameters(gasolineras=100, centros=10, semilla=1234, mul=1)

    # === Configuración del algoritmo ===
    algoritmo = "hill"  # Cambia entre "hill" o "annealing"

    # Parámetros para simulated annealing
    k_sa = 10
    lam_sa = 0.001
    limit_sa = 1000

    # === Construcción de la solución inicial ===
    estado_inicial, tiempo_init, beneficio_init = medir_tiempo_y_beneficio(construir_estado_inicial, params)
    print(f"\nTiempo medio de construcción de la solución inicial: {tiempo_init:.3f} ms")
    if beneficio_init is not None:
        print(f"Beneficio medio de la solución inicial: {beneficio_init:.2f}")
    if hasattr(estado_inicial, 'ben'):
        print(f"BENEFICIO DIARIO (inicial): {estado_inicial.ben:.2f}")

    total, atendidas = contar_peticiones(estado_inicial)
    print(f"Peticiones atendidas (solución inicial): {atendidas}/{total} ({100*atendidas/total:.1f}%)")
    km_total = sum(c.kilometraje for c in estado_inicial.camiones)
    print(f"Kilometraje total (solución inicial): {km_total:.2f} km")

    # === Selección y ejecución del algoritmo ===
    if algoritmo == "hill":
        print("\n===== HILL CLIMBING =====")
        problem = LogisticaProblem(construir_estado_inicial(params))
        t0 = time.time()
        sol = hill_climbing(problem)
        t1 = time.time()
        tiempo = (t1 - t0) * 1000
        beneficio = sol.heuristic() if hasattr(sol, 'heuristic') else None

    elif algoritmo == "annealing":
        print("\n===== SIMULATED ANNEALING =====")
        schedule = exp_schedule(k=k_sa, lam=lam_sa, limit=limit_sa)
        problem = LogisticaProblem(construir_estado_inicial(params))
        t0 = time.time()
        sol = simulated_annealing(problem, schedule)
        t1 = time.time()
        tiempo = (t1 - t0) * 1000
        beneficio = sol.heuristic() if hasattr(sol, 'heuristic') else None

    else:
        raise ValueError("Algoritmo no reconocido. Usa 'hill' o 'annealing'.")

    # === Resultados ===
    print(f"\nTiempo de ejecución ({algoritmo}): {tiempo:.0f} ms")
    if beneficio is not None:
        print(f"Beneficio final ({algoritmo}): {beneficio:.2f}")
    if hasattr(sol, 'ben'):
        print(f"BENEFICIO DIARIO ({algoritmo}): {sol.ben:.2f}")

    if hasattr(sol, 'camiones'):
        total_s, atendidas_s = contar_peticiones(sol)
        print(f"Peticiones atendidas ({algoritmo}): {atendidas_s}/{total_s} ({100*atendidas_s/total_s:.1f}%)")
        km_total_s = sum(c.kilometraje for c in sol.camiones)
        print(f"Kilometraje total ({algoritmo}): {km_total_s:.2f} km")


if __name__ == "__main__":
    main()
