# experimento_operadores.py

import time
from math import sqrt
from pathlib import Path
import random
import numpy as np
import matplotlib.pyplot as plt

from problem_parametres import ProblemParameters
from main_logistics import construir_estado_inicial, contar_peticiones
from LogisticaProblem import LogisticaProblem
from aima.search import hill_climbing

SETS = {
    "A": ["_posibles_add", "_posibles_remove"],
    "B": ["_posibles_reinsert", "_posibles_movimientos"],
    "C": ["_posibles_add", "_posibles_remove", "_posibles_movimientos"],
    "D": ["_posibles_swap"],
    "E": ["_posibles_reinsert", "_posibles_movimientos", "_posibles_swap"],
    "F": ["_posibles_add"],
    "G": ["_posibles_movimientos"],
    "H": ["_posibles_add", "_posibles_movimientos"],
    "I": ["_posibles_remove"],
    "J": ["_posibles_add", "_posibles_reinsert"],
    "K": ["_posibles_reinsert"],
    "Z": ["_posibles_add","_posibles_remove","_posibles_movimientos","_posibles_reinsert","_posibles_swap"],
}

N_GASOLINERAS = 100
N_CENTROS = 10
MULTIPLICIDAD = 1
REPLICAS = 15

def ic95(std: float, n: int) -> float:
    return 0.0 if n <= 1 else 1.96 * std / sqrt(n)

def resumen_metricas(valores):
    arr = np.array(valores, dtype=float)
    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
    return {"mean": mean, "std": std, "ic95": ic95(std, len(arr)),
            "min": float(np.min(arr)), "max": float(np.max(arr)), "n": len(arr)}

def ejecutar_una_replica(activos: list[str], semilla: int) -> dict:
    params = ProblemParameters(
        gasolineras=N_GASOLINERAS,
        centros=N_CENTROS,
        semilla=semilla,
        mul=MULTIPLICIDAD
    )
    estado_inicial = construir_estado_inicial(params)
    estado_inicial.operadores_activos = list(activos)

    problem = LogisticaProblem(estado_inicial)
    t0 = time.time()
    solucion = hill_climbing(problem)
    t1 = time.time()

    ben = getattr(solucion, "ben", None)
    if ben is None:
        ben = -problem.value(solucion)

    try:
        total, atendidas = contar_peticiones(solucion)
        pct = 100 * atendidas / total if total else 0.0
    except:
        total, atendidas, pct = None, None, None

    return {
        "beneficio": float(ben),
        "tiempo_ms": 1000*(t1-t0),
        "atendidas": atendidas,
        "total": total,
        "pct_atendidas": pct,
        "semilla": semilla,
    }

def ejecutar_experimento(sets: dict[str,list[str]], replicas=REPLICAS):
    rng = random.Random(123456)
    semillas = [rng.randint(1,10**9) for _ in range(replicas)]
    resultados = {}

    for nombre, activos in sets.items():
        print(f"\n=== SET {nombre}: {activos} ===")
        muestras = []

        for i, seed in enumerate(semillas, 1):
            res = ejecutar_una_replica(activos, seed)
            muestras.append(res)
            print(f"  réplica {i}/{replicas} | ben={res['beneficio']:.2f} | tiempo={res['tiempo_ms']:.1f} ms")

        resultados[nombre] = {
            "muestras": muestras,
            "resumen": {
                "beneficio": resumen_metricas([m["beneficio"] for m in muestras]),
                "tiempo_ms": resumen_metricas([m["tiempo_ms"] for m in muestras]),
            },
        }

    return resultados


# ===============
#  VISUALIZACIÓN 
# ===============

def plot_barras_con_error(resultados: dict, titulo: str):
    sets = sorted(resultados.keys())
    x = np.arange(len(sets))

    ben_mean = [resultados[s]["resumen"]["beneficio"]["mean"] for s in sets]
    ben_ic95 = [resultados[s]["resumen"]["beneficio"]["ic95"] for s in sets]

    plt.figure(figsize=(8,4))
    plt.bar(x, ben_mean, yerr=ben_ic95, capsize=4)
    plt.xticks(x, sets)
    plt.xlabel("Conjunto")
    plt.ylabel("Beneficio")
    plt.title(titulo + " — Beneficio")
    plt.tight_layout()
    plt.show()

    # tiempo
    tim_mean = [resultados[s]["resumen"]["tiempo_ms"]["mean"] for s in sets]
    tim_ic95 = [resultados[s]["resumen"]["tiempo_ms"]["ic95"] for s in sets]

    plt.figure(figsize=(8,4))
    plt.bar(x, tim_mean, yerr=tim_ic95, capsize=4)
    plt.xticks(x, sets)
    plt.xlabel("Conjunto")
    plt.ylabel("Tiempo (ms)")
    plt.title(titulo + " — Tiempo")
    plt.tight_layout()
    plt.show()

def plot_boxplots(resultados: dict, titulo: str):
    sets = sorted(resultados.keys())

    ben_vals = [[m["beneficio"] for m in resultados[s]["muestras"]] for s in sets]
    plt.figure(figsize=(8,4))
    plt.boxplot(ben_vals, labels=sets, showmeans=True)
    plt.xlabel("Conjunto")
    plt.ylabel("Beneficio")
    plt.title(titulo + " — Beneficio (boxplot)")
    plt.tight_layout()
    plt.show()

    tim_vals = [[m["tiempo_ms"] for m in resultados[s]["muestras"]] for s in sets]
    plt.figure(figsize=(8,4))
    plt.boxplot(tim_vals, labels=sets, showmeans=True)
    plt.xlabel("Conjunto")
    plt.ylabel("Tiempo (ms)")
    plt.title(titulo + " — Tiempo (boxplot)")
    plt.tight_layout()
    plt.show()

def plot_beneficio_vs_tiempo(resultados: dict, titulo: str):
    sets = sorted(resultados.keys())
    x = [resultados[s]["resumen"]["tiempo_ms"]["mean"] for s in sets]
    y = [resultados[s]["resumen"]["beneficio"]["mean"] for s in sets]
    xerr = [resultados[s]["resumen"]["tiempo_ms"]["ic95"] for s in sets]
    yerr = [resultados[s]["resumen"]["beneficio"]["ic95"] for s in sets]

    plt.figure(figsize=(7,5))
    plt.errorbar(x, y, xerr=xerr, yerr=yerr, fmt="o", capsize=3)

    for xi, yi, label in zip(x, y, sets):
        plt.annotate(label, (xi, yi), xytext=(5,5), textcoords="offset points")

    plt.xlabel("Tiempo (ms)")
    plt.ylabel("Beneficio")
    plt.title(titulo + " — Beneficio vs Tiempo")
    plt.tight_layout()
    plt.show()


# ============================================================
# MAIN
# ============================================================

def main():
    print("== Experimento 1: SOLO VISUALIZACIÓN ==")
    resultados = ejecutar_experimento(SETS, replicas=REPLICAS)

    plot_barras_con_error(resultados, "Experimento 1")
    plot_boxplots(resultados, "Experimento 1")
    plot_beneficio_vs_tiempo(resultados, "Experimento 1")

    print("\n== RESUMEN ==")
    for s in sorted(resultados.keys()):
        rb = resultados[s]["resumen"]["beneficio"]
        rt = resultados[s]["resumen"]["tiempo_ms"]
        print(f"{s}: ben={rb['mean']:.2f}±{rb['ic95']:.2f} | t={rt['mean']:.1f}±{rt['ic95']:.1f}")

if __name__ == "__main__":
    main()
