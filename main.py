from Gasolineras import Gasolineras
from CentrosDistribucion import CentrosDistribucion
from Estado import Estado
from Validador import validate_solution

if __name__ == "__main__":
    """
    Código para probar las clases
    No tiene utilidad para la práctica
    """
    s = Gasolineras(100, 1234)
    c = CentrosDistribucion(10, 1, 1234)
    histograma = [0, 0, 0, 0]

    for i in range(len(s.gasolineras)):
        print(f"Gasolinera {i}: {s.gasolineras[i].cx} {s.gasolineras[i].cy}")
        j = 0
        if not s.gasolineras[i].peticiones:
            print("-> Sin peticiones <-")
        for peticion in s.gasolineras[i].peticiones:
            print(f"Peticion {j}: Días {peticion}")
            j += 1
            histograma[peticion] += 1

    print()
    for i in range(4):
        print(f"{histograma[i]} de {i} días")
    print()
    for i in range(len(c.centros)):
        print(f"Centro {i}: {c.centros[i].cx} {c.centros[i].cy}")

    est = Estado(s, c)

    # 1) Listamos todas las peticiones como (valor, gid, pidx)
    all_pets = []
    for gid, g in enumerate(s.gasolineras):
        for pidx, dias in enumerate(g.peticiones):
            val = (100 - 2*dias) * 10  # misma fórmula que valor_peticion()
            all_pets.append((val, gid, pidx))

    # 2) Ordenamos por mayor valor y proximidad a algún centro
    def dist_min_centro(gid):
        gx, gy = s.gasolineras[gid].cx, s.gasolineras[gid].cy
        return min(abs(gx - cc.cx) + abs(gy - cc.cy) for cc in c.centros)

    all_pets.sort(key=lambda t: (-t[0], dist_min_centro(t[1])))

    # 3) Recorremos peticiones: intentamos emparejar y si no, viaje unitario
    for _, gid, pidx in all_pets:
        # buscar el mejor camión (mínimo incremento de km)
        best = None
        for truck in range(len(c.centros)):
            # (a) probar emparejar en un viaje con 1 parada
            for ti, trip in enumerate(est.trips_per_truck[truck]):
                if len(trip.items) == 1:
                    km_old = trip.km
                    val_old = trip.valor               # <-- NUEVO
                    trip.items.append((gid, pidx))
                    est.recompute_viaje(trip)
                    delta = trip.km - km_old
                    # revert provisional
                    trip.items.pop()
                    trip.km = km_old
                    trip.valor = val_old               # <-- NUEVO
                    if est.km_used[truck] + delta <= est.MAX_KM:
                        if best is None or delta < best[0]:
                            best = (delta, ('pair', truck, ti))

            # (b) probar crear viaje unitario si queda cupo
            if len(est.trips_per_truck[truck]) < est.MAX_VIAJES:
                gx, gy = s.gasolineras[gid].cx, s.gasolineras[gid].cy
                cx, cy = c.centros[truck].cx, c.centros[truck].cy
                km_unit = 2 * (abs(gx-cx) + abs(gy-cy))
                if est.km_used[truck] + km_unit <= est.MAX_KM:
                    if best is None or km_unit < best[0]:
                        best = (km_unit, ('single', truck, None))

        # ejecutar la mejor opción hallada (si existe)
        if best:
            _, info = best
            if info[0] == 'pair':
                _, truck, ti = info
                est.pair_into(truck, ti, gid, pidx)
            else:
                _, truck, _ = info
                est.add_single(truck, gid, pidx)

    print("\n=== RESUMEN SOLUCIÓN INICIAL ===")
    print("Viajes por camión:", [len(v) for v in est.trips_per_truck])
    print("Km por camión:    ", est.km_used)
    print("Km totales:", est.total_km, " | Beneficio:", est.total_valor,
          " | Objetivo (beneficio - 2*km):", est.objetivo())
    
    ok, errores, resumen = validate_solution(
    est,
    s,                           # Gasolineras
    c,                           # CentrosDistribucion
    max_trips_per_truck=5,
    max_km_per_truck=640,
    cost_per_km=2,               # cambia si experimentas
    check_totals=True,           # compara con est.total_km / est.total_valor si existen
    atol_km=0                    # tolerancia al comparar km guardados vs recomputados
    )

    print("\n=== VALIDACIÓN ===")
    print("¿Solución válida?:", ok)
    if not ok:
        print("Errores:")
        for e in errores:
            print(" -", e)
    print("Resumen:", resumen)