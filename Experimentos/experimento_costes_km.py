# experimento_coste_km_solo_pantalla.py
# Experimento 6: Aumento del coste por kilómetro
# - Reutiliza el pipeline del Exp.1 (mismas semillas por configuración)
# - No modifica tu código base: subclase de EstadoExtendido con coste_km paramétrico
# - Mide beneficio, distancia media y tiempo; SOLO MUESTRA GRÁFICOS EN PANTALLA

import time
from math import sqrt
import random
import numpy as np
import matplotlib.pyplot as plt

from problem_parametres import ProblemParameters
from main_logistics import construir_estado_inicial
from LogisticaProblem import LogisticaProblem
from aima.search import hill_climbing

# ---------- Subtipo de estado con coste/km paramétrico ----------
from EstadoExtendido import EstadoExtendido, factor_precio_por_dias

class EstadoCosteKm(EstadoExtendido):
    def __init__(self, gasolineras, centros, camiones, coste_km: float = 2.0):
        super().__init__(gasolineras, centros, camiones)
        self.coste_km = float(coste_km)

    def copy(self) -> "EstadoCosteKm":
        # Copia segura heredando operadores activos e índice
        cam_copy = [type(self.camiones[0])(c.id, c.kilometraje, [list(v) for v in c.ruta])
                    for c in self.camiones]
        new = EstadoCosteKm(self.gasolineras, self.centros, cam_copy, coste_km=self.coste_km)
        new.operadores_activos = list(getattr(self, "operadores_activos", []))
        new._pos_index = None
        return new

    def heuristic(self) -> float:
        # Misma lógica que EstadoExtendido, sustituyendo 2.0 por self.coste_km
        atendidas = set()
        beneficio = 0.0
        for c in self.camiones:
            for viaje in c.ruta:
                for s in viaje:
                    atendidas.add(s)
                    gid, pidx = s
                    dias = self.gasolineras.gasolineras[gid].peticiones[pidx]
                    beneficio += 1000.0 * factor_precio_por_dias(dias)

        perdida = 0.0
        for gid, g in enumerate(self.gasolineras.gasolineras):
            for pidx, dias in enumerate(g.peticiones):
                s = (gid, pidx)
                if s not in atendidas:
                    factor_hoy = factor_precio_por_dias(dias)
                    factor_mana = factor_precio_por_dias(dias + 1)
                    perdida += 1000.0 * (factor_hoy - factor_mana)

        distancia_total = sum(c.kilometraje for c in self.camiones)
        self.ben = beneficio - self.coste_km * float(distancia_total) - perdida

        # AIMA minimiza heuristic(): devolvemos "coste"
        return -(beneficio/5 - perdida - (self.coste_km * float(distancia_total)))


# =========================
# Configuración
# =========================
N_GASOLINERAS = 100
N_CENTROS = 10
MULTIPLICIDAD = 1
REPLICAS = 10
COSTES = [2.0, 4.0, 8.0, 16.0]  

# =========================
# Utilidades estadísticas
# =========================
def ic95(std: float, n: int) -> float:
    return 0.0 if n <= 1 else 1.96 * std / sqrt(n)

def resumen_metricas(valores):
    arr = np.array(valores, dtype=float)
    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
    return {"mean": mean, "std": std, "ic95": ic95(std, len(arr)),
            "min": float(np.min(arr)), "max": float(np.max(arr)), "n": len(arr)}

# =========================
# Núcleo de ejecución
# =========================
def _wrap_estado_con_coste(est: EstadoExtendido, coste_km: float) -> EstadoCosteKm:
    """Convierte EstadoExtendido -> EstadoCosteKm heredando rutas, km y operadores."""
    cam_copy = [type(est.camiones[0])(c.id, c.kilometraje, [list(v) for v in c.ruta])
                for c in est.camiones]
    new = EstadoCosteKm(est.gasolineras, est.centros, cam_copy, coste_km=coste_km)
    new.operadores_activos = list(getattr(est, "operadores_activos", []))
    return new

def ejecutar_una_replica(coste_km: float, semilla: int) -> dict:
    params = ProblemParameters(gasolineras=N_GASOLINERAS, centros=N_CENTROS,
                               semilla=semilla, mul=MULTIPLICIDAD)
    est0 = construir_estado_inicial(params)              # EstadoExtendido base
    estC = _wrap_estado_con_coste(est0, coste_km)        # Misma solución/operadores + coste_km
    # Forzamos el conjunto C = {add, remove, move}
    estC.operadores_activos = ["_posibles_add", "_posibles_remove", "_posibles_movimientos"]

    problem = LogisticaProblem(estC)
    t0 = time.time()
    sol = hill_climbing(problem)
    t1 = time.time()

    # Forzamos el cálculo de 'ben' con el coste/km vigente
    _ = sol.heuristic() if hasattr(sol, "heuristic") else None
    beneficio = getattr(sol, "ben", None)
    if beneficio is None:
        beneficio = -problem.value(sol)

    # Distancia total recorrida (km Manhattan del modelo)
    distancia_total = sum(c.kilometraje for c in sol.camiones)

    return {
        "beneficio": float(beneficio),
        "tiempo_ms": float((t1 - t0) * 1000.0),
        "distancia": float(distancia_total),
        "semilla": semilla,
        "coste_km": float(coste_km),
    }

def ejecutar_experimento_coste(costes=COSTES, replicas=REPLICAS) -> dict:
    rng = random.Random(123456)                    # mismas semillas para todos los niveles de coste
    semillas = [rng.randint(1, 10**9) for _ in range(replicas)]
    resultados = {}

    for c in costes:
        muestras = []
        print(f"\n=== Coste/km = {c:.2f} ===")
        for i, seed in enumerate(semillas, 1):
            res = ejecutar_una_replica(c, seed)
            muestras.append(res)
            print(f"  réplica {i:02d}/{replicas} | t={res['tiempo_ms']:.1f} ms | "
                  f"ben={res['beneficio']:.2f} | km={res['distancia']:.1f}")
        resultados[c] = {
            "muestras": muestras,
            "resumen": {
                "beneficio": resumen_metricas([m["beneficio"] for m in muestras]),
                "tiempo_ms": resumen_metricas([m["tiempo_ms"] for m in muestras]),
                "distancia": resumen_metricas([m["distancia"] for m in muestras]),
            },
        }
    return resultados

# =========================
# PLOTS — SOLO PANTALLA
# =========================
def plot_linea(resultados: dict, titulo: str):
    xs = sorted(resultados.keys())
    ben_mean = [resultados[c]["resumen"]["beneficio"]["mean"] for c in xs]
    ben_ic95 = [resultados[c]["resumen"]["beneficio"]["ic95"] for c in xs]
    dst_mean = [resultados[c]["resumen"]["distancia"]["mean"] for c in xs]
    dst_ic95 = [resultados[c]["resumen"]["distancia"]["ic95"] for c in xs]
    t_mean = [resultados[c]["resumen"]["tiempo_ms"]["mean"] for c in xs]
    t_ic95 = [resultados[c]["resumen"]["tiempo_ms"]["ic95"] for c in xs]

    # Beneficio vs coste
    plt.figure(figsize=(7.2, 4.2))
    plt.errorbar(xs, ben_mean, yerr=ben_ic95, fmt='o-', capsize=3)
    plt.xlabel("Coste por kilómetro (€)")
    plt.ylabel("Beneficio (media ± IC95)")
    plt.title(f"{titulo} — Beneficio vs coste/km")
    plt.tight_layout()
    plt.show()

    # Distancia vs coste
    plt.figure(figsize=(7.2, 4.2))
    plt.errorbar(xs, dst_mean, yerr=dst_ic95, fmt='o-', capsize=3)
    plt.xlabel("Coste por kilómetro (€)")
    plt.ylabel("Distancia media total (km) ± IC95")
    plt.title(f"{titulo} — Distancia vs coste/km")
    plt.tight_layout()
    plt.show()

    # Tiempo vs coste
    plt.figure(figsize=(7.2, 4.2))
    plt.errorbar(xs, t_mean, yerr=t_ic95, fmt='o-', capsize=3)
    plt.xlabel("Coste por kilómetro (€)")
    plt.ylabel("Tiempo (ms) ± IC95")
    plt.title(f"{titulo} — Tiempo vs coste/km")
    plt.tight_layout()
    plt.show()

def plot_boxplots_por_coste(resultados: dict, titulo: str):
    xs = sorted(resultados.keys())

    # Beneficio
    ben_vals = [[m["beneficio"] for m in resultados[c]["muestras"]] for c in xs]
    plt.figure(figsize=(7.5, 4.2))
    plt.boxplot(ben_vals, labels=[f"{c:.1f}" for c in xs], showmeans=True)
    plt.xlabel("Coste por kilómetro (€)")
    plt.ylabel("Beneficio")
    plt.title(f"{titulo} — Beneficio (boxplot 15 réplicas)")
    plt.tight_layout()
    plt.show()

    # Distancia
    dst_vals = [[m["distancia"] for m in resultados[c]["muestras"]] for c in xs]
    plt.figure(figsize=(7.5, 4.2))
    plt.boxplot(dst_vals, labels=[f"{c:.1f}" for c in xs], showmeans=True)
    plt.xlabel("Coste por kilómetro (€)")
    plt.ylabel("Distancia total (km)")
    plt.title(f"{titulo} — Distancia (boxplot 15 réplicas)")
    plt.tight_layout()
    plt.show()

def plot_tradeoff_beneficio_vs_distancia(resultados: dict, titulo: str):
    xs = sorted(resultados.keys())
    x = [resultados[c]["resumen"]["distancia"]["mean"] for c in xs]
    y = [resultados[c]["resumen"]["beneficio"]["mean"] for c in xs]
    xerr = [resultados[c]["resumen"]["distancia"]["ic95"] for c in xs]
    yerr = [resultados[c]["resumen"]["beneficio"]["ic95"] for c in xs]

    plt.figure(figsize=(7.2, 4.6))
    plt.errorbar(x, y, xerr=xerr, yerr=yerr, fmt='o', capsize=3)
    for xi, yi, c in zip(x, y, xs):
        plt.annotate(f"{c:.1f}€", (xi, yi), xytext=(5, 5), textcoords="offset points")
    plt.xlabel("Distancia media (km) ± IC95")
    plt.ylabel("Beneficio medio ± IC95")
    plt.title(f"{titulo} — Trade-off Beneficio vs Distancia")
    plt.tight_layout()
    plt.show()

def plot_cambios_relativos_vs_base(resultados: dict, coste_base: float, titulo: str):
    """
    Barras con IC95 sobre el CAMBIO RELATIVO respecto al coste_base.
    Usa diferencias EMPAREJADAS por réplica (misma semilla) → IC95 correcto.
    """
    if coste_base not in resultados:
        raise ValueError("El coste_base no está en resultados.")

    xs = sorted(resultados.keys())
    xs_sin_base = [c for c in xs if c != coste_base]

    n = len(resultados[coste_base]["muestras"])

    ben_delta = []
    dst_delta = []
    for c in xs_sin_base:
        delta_b = []
        delta_d = []
        base_m = resultados[coste_base]["muestras"]
        cmp_m = resultados[c]["muestras"]
        for i in range(n):
            b0 = base_m[i]["beneficio"]; b1 = cmp_m[i]["beneficio"]
            d0 = base_m[i]["distancia"]; d1 = cmp_m[i]["distancia"]
            delta_b.append(100.0 * (b1 - b0) / abs(b0) if b0 else 0.0)
            delta_d.append(100.0 * (d1 - d0) / abs(d0) if d0 else 0.0)
        ben_delta.append(delta_b)
        dst_delta.append(delta_d)

    def _mean_std_ic95(arr):
        arr = np.array(arr, dtype=float)
        m = float(np.mean(arr)); s = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
        ic = 1.96 * s / np.sqrt(len(arr)) if len(arr) > 1 else 0.0
        return m, s, ic

    ben_mean = []; ben_ic = []
    dst_mean = []; dst_ic = []
    for db, dd in zip(ben_delta, dst_delta):
        m_b, _, ic_b = _mean_std_ic95(db)
        m_d, _, ic_d = _mean_std_ic95(dd)
        ben_mean.append(m_b); ben_ic.append(ic_b)
        dst_mean.append(m_d); dst_ic.append(ic_d)

    x = np.arange(len(xs_sin_base))
    labels = [f"{c:.1f}" for c in xs_sin_base]

    # Beneficio relativo
    plt.figure(figsize=(7.2, 4.2))
    plt.bar(x, ben_mean, yerr=ben_ic, capsize=4)
    plt.xticks(x, labels)
    plt.axhline(0, linewidth=1)
    plt.xlabel("Coste por kilómetro (€) — respecto a base")
    plt.ylabel("Δ Beneficio (%)  ± IC95 (emparejado)")
    plt.title(f"{titulo} — Cambio relativo de Beneficio vs {coste_base:.1f}€")
    plt.tight_layout()
    plt.show()

    # Distancia relativa
    plt.figure(figsize=(7.2, 4.2))
    plt.bar(x, dst_mean, yerr=dst_ic, capsize=4)
    plt.xticks(x, labels)
    plt.axhline(0, linewidth=1)
    plt.xlabel("Coste por kilómetro (€) — respecto a base")
    plt.ylabel("Δ Distancia (%)  ± IC95 (emparejado)")
    plt.title(f"{titulo} — Cambio relativo de Distancia vs {coste_base:.1f}€")
    plt.tight_layout()
    plt.show()

# =========================
# Main
# =========================
def main():
    print("== Experimento 6: Aumento del coste por kilómetro ==")
    print(f"Escenario: centros={N_CENTROS}, gasolineras={N_GASOLINERAS}, operadores=C\n")

    resultados = ejecutar_experimento_coste(COSTES, replicas=REPLICAS)

    # Figuras (solo pantalla)
    plot_linea(resultados, "Experimento 6. Aumento del coste por km")
    plot_boxplots_por_coste(resultados, "Experimento 6. Aumento del coste por km")
    plot_tradeoff_beneficio_vs_distancia(resultados, "Experimento 6. Aumento del coste por km")
    plot_cambios_relativos_vs_base(
        resultados, coste_base=2.0,
        titulo="Experimento 6. Aumento del coste por km"
    )

    # Resumen consola
    print("\n== Resumen (media ± IC95%) ==")
    for c in sorted(resultados.keys()):
        rb = resultados[c]["resumen"]["beneficio"]
        rd = resultados[c]["resumen"]["distancia"]
        rt = resultados[c]["resumen"]["tiempo_ms"]
        print(f"Coste {c:.2f}: Beneficio = {rb['mean']:.2f} ± {rb['ic95']:.2f} | "
              f"Dist = {rd['mean']:.1f} ± {rd['ic95']:.1f} km | "
              f"Tiempo = {rt['mean']:.1f} ± {rt['ic95']:.1f} ms")

if __name__ == "__main__":
    main()