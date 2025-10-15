# validator.py
from typing import List, Tuple, Optional, Iterable

# ---- Ajusta aquí si tu enunciado usa otra fórmula ----
def default_benefit_fn(dias: int) -> int:
    """
    Beneficio por petición servida hoy en función de 'días pendientes'.
    Por defecto: 1000 * (100 - 2*dias) / 100  (entero)
    """
    return max(0, (100 - 2*dias) * 10)

DEFAULT_COST_PER_KM = 2

def manhattan(a: Tuple[int,int], b: Tuple[int,int]) -> int:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# ----- Extractores de datos para ser agnóstico a tu estructura -----

def _get_center_xy(centros, truck_idx: int) -> Tuple[int,int]:
    """centros.centros[truck_idx] con attrs cx, cy"""
    c = centros.centros[truck_idx]
    return (c.cx, c.cy)

def _get_station_xy(gasolineras, gid: int) -> Tuple[int,int]:
    """gasolineras.gasolineras[gid] con attrs cx, cy"""
    g = gasolineras.gasolineras[gid]
    return (g.cx, g.cy)

def _get_station_days(gasolineras, gid: int, pidx: int) -> int:
    """Devuelve días pendientes de la petición local pidx en la gasolinera gid"""
    return gasolineras.gasolineras[gid].peticiones[pidx]

def _iterate_trips(sol) -> Tuple[int, Iterable]:
    """
    Devuelve (num_trucks, iterable_de_listas_de_viajes)
    Soporta:
      - sol.trips_per_truck -> List[List[Viaje]]
      - sol.camiones[i].viajes -> List[Viaje]
      - sol.camiones[i].recorridos -> List[List[(gid,pidx)]] (sin objeto Viaje)
    """
    if hasattr(sol, "trips_per_truck"):
        return len(sol.trips_per_truck), sol.trips_per_truck
    if hasattr(sol, "camiones"):
        num_trucks = len(sol.camiones)
        # Intentar .viajes (objeto Viaje con .items)
        if num_trucks and hasattr(sol.camiones[0], "viajes"):
            lst = []
            for c in sol.camiones:
                lst.append(getattr(c, "viajes"))
            return num_trucks, lst
        # Intentar .recorridos (lista de listas de (gid,pidx) o de gid suelto)
        if num_trucks and hasattr(sol.camiones[0], "recorridos"):
            lst = []
            for c in sol.camiones:
                # Adaptador: cada recorrido lo convertimos a objeto sencillo con .items
                trips = []
                for r in c.recorridos:
                    # r podría ser [gid] o [(gid,pidx), ...]
                    items = []
                    for x in r:
                        if isinstance(x, tuple) and len(x) == 2:
                            items.append((x[0], x[1]))
                        else:
                            # si solo tienes gasolinera, asumimos pidx=0
                            items.append((x, 0))
                    trips.append(SimpleTrip(c.id, items))
                lst.append(trips)
            return num_trucks, lst
    raise ValueError("No reconozco la estructura de viajes en la solución.")

class SimpleTrip:
    """Wrapper mínimo para uniformizar la interfaz (cuando no hay clase Viaje real)."""
    __slots__ = ("truck", "items", "km", "valor")
    def __init__(self, truck: int, items: List[Tuple[int,int]]):
        self.truck = truck
        self.items = items
        self.km = 0
        self.valor = 0

# ---- Cálculo de km y valor por viaje (intenta el mejor orden para 2 paradas) ----

def _recompute_trip(trip, gasolineras, centros,
                    benefit_fn=default_benefit_fn) -> Tuple[int,int]:
    """Devuelve (km, valor) recomputados desde cero para este viaje."""
    cx, cy = _get_center_xy(centros, trip.truck)

    def val(gid: int, pidx: int) -> int:
        return benefit_fn(_get_station_days(gasolineras, gid, pidx))

    if len(trip.items) == 1:
        gid, pidx = trip.items[0]
        gx, gy = _get_station_xy(gasolineras, gid)
        km = 2 * manhattan((cx,cy), (gx,gy))
        return km, val(gid, pidx)

    # Dos paradas: probamos ambos órdenes
    (g1, i1), (g2, i2) = trip.items
    x1,y1 = _get_station_xy(gasolineras, g1)
    x2,y2 = _get_station_xy(gasolineras, g2)
    a = manhattan((cx,cy),(x1,y1)) + manhattan((x1,y1),(x2,y2)) + manhattan((x2,y2),(cx,cy))
    b = manhattan((cx,cy),(x2,y2)) + manhattan((x2,y2),(x1,y1)) + manhattan((x1,y1),(cx,cy))
    km = a if a < b else b
    return km, (val(g1, i1) + val(g2, i2))

# ---- Validador principal ----

def validate_solution(sol,
                      gasolineras,
                      centros,
                      *,
                      max_trips_per_truck: int = 5,
                      max_km_per_truck: int = 640,
                      cost_per_km: int = DEFAULT_COST_PER_KM,
                      benefit_fn=default_benefit_fn,
                      check_totals: bool = True,
                      atol_km: int = 0) -> Tuple[bool, List[str], dict]:
    """
    Devuelve (is_valid, errores, resumen_dict)
    - Verifica TODAS las constraints:
      • nº viajes por camión, km por camión
      • 1–2 paradas por viaje
      • no duplicar peticiones
      • índices válidos
      • consistencia de km/beneficio (recomputado)
    - Opcionalmente compara totales con sol (si tiene campos totales).
    """
    errors: List[str] = []
    seen: set[Tuple[int,int]] = set()

    # Soportar Estado y Solucion
    try:
        num_trucks, trips_lists = _iterate_trips(sol)
    except Exception as e:
        return False, [f"Estructura no reconocida: {e}"], {}

    # Consistencias declaradas (si existen)
    declared_total_km = getattr(sol, "total_km", getattr(sol, "km_totales", None))
    declared_total_val = getattr(sol, "total_valor", getattr(sol, "beneficio_total", None))

    # Validaciones
    recomputed_km_per_truck = [0]*num_trucks
    recomputed_trips_per_truck = [0]*num_trucks
    recomputed_total_km = 0
    recomputed_total_val = 0

    # 1) Iterar camiones y viajes
    for t_idx in range(num_trucks):
        trips = trips_lists[t_idx]
        recomputed_trips_per_truck[t_idx] = len(trips)
        # restricción: nº viajes
        if len(trips) > max_trips_per_truck:
            errors.append(f"Camión {t_idx}: {len(trips)} viajes (> {max_trips_per_truck}).")

        for v_idx, trip in enumerate(trips):
            # restricción: 1–2 paradas
            if len(trip.items) < 1 or len(trip.items) > 2:
                errors.append(f"Camión {t_idx}, viaje {v_idx}: {len(trip.items)} paradas (debe ser 1 o 2).")
                continue

            # índices válidos + no duplicados
            for (gid, pidx) in trip.items:
                if gid < 0 or gid >= len(gasolineras.gasolineras):
                    errors.append(f"Camión {t_idx}, viaje {v_idx}: gasolinera {gid} inexistente.")
                    continue
                if pidx < 0 or pidx >= len(gasolineras.gasolineras[gid].peticiones):
                    errors.append(f"Camión {t_idx}, viaje {v_idx}: petición {pidx} no existe en gasolinera {gid}.")
                    continue
                if (gid, pidx) in seen:
                    errors.append(f"Petición repetida: ({gid},{pidx}) usada más de una vez.")
                seen.add((gid, pidx))

            # km/valor recomputados (consistencia de cálculo)
            km_v, val_v = _recompute_trip(trip, gasolineras, centros, benefit_fn)
            recomputed_km_per_truck[t_idx] += km_v
            recomputed_total_km += km_v
            recomputed_total_val += val_v

            # Si el viaje trae km/valor “guardado”, comprobar (tolerancia atol_km)
            if hasattr(trip, "km"):
                if abs((trip.km or 0) - km_v) > atol_km:
                    errors.append(f"Camión {t_idx}, viaje {v_idx}: km almacenado={getattr(trip,'km',None)} "
                                  f"≠ km recomputado={km_v}.")
            if hasattr(trip, "valor"):
                if (trip.valor or 0) != val_v:
                    errors.append(f"Camión {t_idx}, viaje {v_idx}: valor almacenado={getattr(trip,'valor',None)} "
                                  f"≠ valor recomputado={val_v}.")

        # restricción: km por camión
        if recomputed_km_per_truck[t_idx] > max_km_per_truck:
            errors.append(f"Camión {t_idx}: {recomputed_km_per_truck[t_idx]} km (> {max_km_per_truck}).")

    # 2) Totales y objetivo
    recomputed_objective = recomputed_total_val - cost_per_km * recomputed_total_km

    # si la solución declara totales, comprarlos
    if check_totals and declared_total_km is not None:
        if declared_total_km != recomputed_total_km:
            errors.append(f"km_totales declarados={declared_total_km} ≠ recomputados={recomputed_total_km}.")
    if check_totals and declared_total_val is not None:
        if declared_total_val != recomputed_total_val:
            errors.append(f"beneficio_total declarado={declared_total_val} ≠ recomputado={recomputed_total_val}.")

    is_valid = len(errors) == 0
    summary = {
        "km_por_camion": recomputed_km_per_truck,
        "viajes_por_camion": recomputed_trips_per_truck,
        "km_totales": recomputed_total_km,
        "beneficio_total": recomputed_total_val,
        "objetivo": recomputed_objective,
        "num_peticiones_serv": len(seen),
    }
    return is_valid, errors, summary
