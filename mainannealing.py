from Gasolineras import Gasolineras
from CentrosDistribucion import CentrosDistribucion
from Camion import Camion
from SolucionBase import SolucionBase
from EstadoExtendido import EstadoExtendido
from LogisticaProblem import LogisticaProblem
from problem_parametres import ProblemParameters
from aima.search import hill_climbing, simulated_annealing, exp_schedule
import time
import random
import matplotlib.pyplot as plt


def construir_estado_inicial(params: ProblemParameters):
    gas = Gasolineras(num_gasolineras=params.gasolineras, seed=params.semilla)
    centers = CentrosDistribucion(num_centros=params.centros, multiplicidad=params.multiplicidad, seed=params.semilla)
    camiones = [Camion(camion_id=i, k=0, viajes=[]) for i in range(len(centers.centros))]
    estado = EstadoExtendido(gas, centers, camiones)
    SolucionBase(estado).build()
    return estado


def contar_peticiones(est: EstadoExtendido):
    total = sum(len(g.peticiones) for g in est.gasolineras.gasolineras)
    atendidas = sum(len(v) for c in est.camiones for v in c.ruta for _ in v)
    return total, atendidas


def main():
    params_base = ProblemParameters(gasolineras=100, centros=10, mul=1, semilla=0)
    algoritmo = "annealing"  # "hill" o "annealing"
    repeticiones = 10

    seeds = [1] #Poner lista de de semillas

    k_sa = 10
    lam_sa = 0.01
    limit_sa = 500

    beneficios = []
    kms = []
    tiempos = []
    heuristicos = []
    atendidas_percent = []

    historial_por_repeticion = []

    for i in range(repeticiones):
        params = params_base
        params.semilla = seeds[i % len(seeds)]  

        estado_inicial = construir_estado_inicial(params)
        total, atendidas = contar_peticiones(estado_inicial)

        historial = []

        class LogisticaProblemConHistorial(LogisticaProblem):
            def value(self, state):
                h = super().value(state)
                historial.append(-h)
                return h

        problem = LogisticaProblemConHistorial(estado_inicial)

        t0 = time.time()
        if algoritmo == "hill":
            sol = hill_climbing(problem)
        else:  # annealing
            schedule = exp_schedule(k=k_sa, lam=lam_sa, limit=limit_sa)
            sol = simulated_annealing(problem, schedule)
        t1 = time.time()

        tiempo = (t1 - t0) * 1000  # ms
        tiempos.append(tiempo)

        heuristico = sol.heuristic()
        heuristicos.append(heuristico)

        beneficio = sol.ben if hasattr(sol, 'ben') else heuristico
        beneficios.append(beneficio)

        total_s, atendidas_s = contar_peticiones(sol)
        atendidas_percent.append(100.0 * atendidas_s / total_s)

        km_total_s = sum(c.kilometraje for c in sol.camiones)
        kms.append(km_total_s)

        historial_por_repeticion.append(historial)


    print(f"\nResultados promedio tras {repeticiones} repeticiones:")
    print(f"Tiempo medio de ejecución: {sum(tiempos)/len(tiempos):.2f} ms")
    print(f"Beneficio medio (ben): {sum(beneficios)/len(beneficios):.2f}")
    print(f"Heurística media: {sum(heuristicos)/len(heuristicos):.2f}")
    print(f"Kilometraje total medio: {sum(kms)/len(kms):.2f} km")
    print(f"Porcentaje medio de peticiones atendidas: {sum(atendidas_percent)/len(atendidas_percent):.2f} %")


    plt.figure(figsize=(20,20))
    for idx, hist in enumerate(historial_por_repeticion):
        plt.plot(hist, marker='o', label=f'Repetición {idx+1}')
    plt.title(f'Evolución de la heurística ({algoritmo})')
    plt.xlabel('Paso')
    plt.ylabel('Valor heurística')
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
