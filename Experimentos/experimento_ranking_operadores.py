# experimento_ranking_operadores.py
# Experimento Extra: Ranking de operadores usados para los conjuntos C, H y Z

import time
import random
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D   

from problem_parametres import ProblemParameters
from main_logistics import construir_estado_inicial, contar_peticiones
from LogisticaProblem import LogisticaProblem
from aima.search import hill_climbing
from EstadoExtendido import EstadoExtendido


# Configuración

SETS_CHZ = {
    "C": ["_posibles_add", "_posibles_remove", "_posibles_movimientos"],
    "H": ["_posibles_add", "_posibles_movimientos"],
    "Z": ["_posibles_add", "_posibles_remove", "_posibles_movimientos",
          "_posibles_reinsert", "_posibles_swap"],
}

N_GASOLINERAS = 100
N_CENTROS = 15
MULTIPLICIDAD = 1
REPLICAS = 10

# Operadores que queremos trackear
OPERADORES_POSIBLES = [
    "_posibles_add",
    "_posibles_remove",
    "_posibles_movimientos",
    "_posibles_reinsert",
    "_posibles_swap",
]

# Para restaurar métodos originales tras el parcheo
ORIGINAL_METHODS = {}


# Parcheo de EstadoExtendido para contar operadores


def patch_operadores(counter: dict[str, int]):
    """
    Envuelve los métodos de generación de operadores de EstadoExtendido
    para incrementar un contador CADA VEZ que generan un vecino (yield),
    no solo por llamada a la función.
    """
    for nombre in OPERADORES_POSIBLES:
        if not hasattr(EstadoExtendido, nombre):
            continue
        orig = getattr(EstadoExtendido, nombre)
        ORIGINAL_METHODS[nombre] = orig

        def make_wrapper(f_original, op_name):
            def wrapper(self, *args, **kwargs):
                gen = f_original(self, *args, **kwargs)
                for op in gen:
                    counter[op_name] += 1
                    yield op
            return wrapper

        wrapped = make_wrapper(orig, nombre)
        setattr(EstadoExtendido, nombre, wrapped)


def unpatch_operadores():
    """Restaura los métodos originales de EstadoExtendido."""
    for nombre, f_original in ORIGINAL_METHODS.items():
        setattr(EstadoExtendido, nombre, f_original)
    ORIGINAL_METHODS.clear()


# Núcleo: una réplica con conteo de operadores

def ejecutar_una_replica_con_conteo(activos: list[str], semilla: int) -> dict:
    # Contador local de operadores para esta réplica
    contador_ops = defaultdict(int)
    patch_operadores(contador_ops)

    try:
        params = ProblemParameters(
            gasolineras=N_GASOLINERAS,
            centros=N_CENTROS,
            semilla=semilla,
            mul=MULTIPLICIDAD,
        )
        estado_inicial = construir_estado_inicial(params)
        estado_inicial.operadores_activos = list(activos)

        problem = LogisticaProblem(estado_inicial)

        t0 = time.time()
        solucion = hill_climbing(problem)
        t1 = time.time()

        _ = solucion.heuristic() if hasattr(solucion, "heuristic") else None
        beneficio = getattr(solucion, "ben", None)
        if beneficio is None:
            beneficio = -problem.value(solucion)

        try:
            total, atendidas = contar_peticiones(solucion)
            pct = 100.0 * atendidas / total if total else 0.0
        except Exception:
            total, atendidas, pct = None, None, None

        return {
            "beneficio": float(beneficio),
            "tiempo_ms": float((t1 - t0) * 1000.0),
            "atendidas": atendidas,
            "total": total,
            "pct_atendidas": pct,
            "semilla": semilla,
            "uso_operadores": dict(contador_ops),
        }
    finally:
        # restaurar siempre los métodos originales
        unpatch_operadores()


# Bucle de experimento 

def ejecutar_experimento_ranking(replicas: int = REPLICAS) -> dict:
    rng = random.Random(123456)
    semillas = [rng.randint(1, 10**9) for _ in range(replicas)]
    resultados = {}

    for nombre_set, activos in SETS_CHZ.items():
        print(f"\n=== Set {nombre_set}: {activos} ===")
        muestras = []
        for i, seed in enumerate(semillas, 1):
            res = ejecutar_una_replica_con_conteo(activos, seed)
            muestras.append(res)
            pct_str = (
                f"{res['pct_atendidas']:.1f}%"
                if res["pct_atendidas"] is not None
                else "n/a"
            )
            print(
                f"  réplica {i:02d}/{replicas} | ben={res['beneficio']:.2f} | "
                f"att={res['atendidas']}/{res['total']} ({pct_str})"
            )
        resultados[nombre_set] = {"muestras": muestras}

    return resultados


# Ranking y resumen por consola

def imprimir_ranking_operadores(resultados: dict):
    print("\n== Ranking global de operadores por conjunto (sobre todas las réplicas) ==")

    for s in sorted(resultados.keys()):
        acumulado = defaultdict(int)
        for m in resultados[s]["muestras"]:
            for op, cnt in m["uso_operadores"].items():
                acumulado[op] += cnt

        total = sum(acumulado.values())
        ranking = sorted(acumulado.items(), key=lambda x: x[1], reverse=True)

        print(f"\n-- Set {s} --")
        if total == 0:
            print("  (sin llamadas registradas a operadores)")
            continue

        for op, cnt in ranking:
            pct = 100.0 * cnt / total
            print(f"  {op:22s}  {cnt:8d}  ({pct:5.1f}%)")


# Histograma 3D 

def plot_histograma_3d(resultados: dict):
    """
    Histograma 3D:
    - Eje X: sets (C, H, Z)
    - Eje Y: índice de operador (sin nombres)
    - Eje Z: uso medio (nº de vecinos generados por réplica)
    Cada operador tiene un color y aparece en la leyenda.
    """
    sets = sorted(resultados.keys())          # ['C', 'H', 'Z']
    operadores = OPERADORES_POSIBLES[:]       # en el orden definido

    # Uso medio por réplica para cada set y operador
    uso_medio = {s: {op: 0.0 for op in operadores} for s in sets}
    for s in sets:
        muestras = resultados[s]["muestras"]
        n_rep = len(muestras) or 1

        acumulado = {op: 0 for op in operadores}
        for m in muestras:
            uso_ops = m["uso_operadores"]
            for op in operadores:
                acumulado[op] += uso_ops.get(op, 0)

        for op in operadores:
            uso_medio[s][op] = acumulado[op] / n_rep

    xs = np.arange(len(sets))        # 0..2
    ys = np.arange(len(operadores))  # 0..4

    dx = 0.25
    dy = 0.25

    # Colores por operador
    colores = plt.cm.tab10(np.linspace(0, 1, len(operadores)))

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection="3d")

    # Dibujar barras: color según operador (y)
    for yi, op in enumerate(operadores):
        for xi, s in enumerate(sets):
            z = uso_medio[s][op]
            ax.bar3d(
                xi, yi, 0,
                dx, dy, z,
                color=colores[yi],
                alpha=0.9,
                shade=True,
            )

    ax.view_init(elev=25, azim=40)

    # Eje X: sets
    ax.set_xticks(xs + dx / 2)
    ax.set_xticklabels(sets)
    ax.set_xlabel("Set de operadores")

    # Eje Y: solo índice (sin nombres de operadores)
    ax.set_yticks(ys + dy / 2)
    ax.set_yticklabels([])      # <- quitamos los nombres
    ax.set_ylabel("Operador")

    # Eje Z
    ax.set_zlabel("Uso medio (nº de vecinos)")
    ax.set_title("Histograma 3D — Uso medio de operadores por set")

    # Leyenda con nombres de operadores
    legend_elems = [
        plt.Rectangle((0, 0), 1, 1, color=colores[i], label=operadores[i])
        for i in range(len(operadores))
    ]
    ax.legend(
        handles=legend_elems,
        labels=operadores,
        loc="center left",
        bbox_to_anchor=(1.05, 0.5)
    )


    plt.subplots_adjust(right=0.78, left=0.08, bottom=0.15)
    plt.show()


# Main

def main():
    print("== Experimento Extra: Ranking de operadores usados (C, H, Z) ==")
    print(f"Escenario: centros={N_CENTROS}, camiones={N_CENTROS}, gasolineras={N_GASOLINERAS}\n")

    resultados = ejecutar_experimento_ranking(replicas=REPLICAS)
    imprimir_ranking_operadores(resultados)
    plot_histograma_3d(resultados)


if __name__ == "__main__":
    main()
