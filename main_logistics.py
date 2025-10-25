# main_logistics.py
from Gasolineras import Gasolineras
from CentrosDistribucion import CentrosDistribucion
from Camion import Camion
from SolucionBase import SolucionBase
from EstadoExtendido import EstadoExtendido
from LogisticaProblem import LogisticaProblem

from aima.search import hill_climbing

def construir_estado_inicial():
    gas = Gasolineras(num_gasolineras=10, seed=42)
    centers = CentrosDistribucion(num_centros=1, multiplicidad=1, seed=133)
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
    print(f"Heurística (coste estimado): {est.heuristic():.2f}")


def main():
    estado_inicial = construir_estado_inicial()
    imprimir_estado(estado_inicial)

    problem = LogisticaProblem(estado_inicial)

    # === 1. Hill Climbing ===
    print("\n===== HILL CLIMBING =====")
    sol_hc = hill_climbing(problem)
    imprimir_estado(sol_hc)

if __name__ == "__main__":
    main()
