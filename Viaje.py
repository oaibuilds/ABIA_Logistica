from Escenario import Escenario
from typing import List, Tuple

@dataclass
class Viaje:
    truck: int                                   # id de camión (índice en center_xy)
    items: List[Tuple[int,int]]                  # [(gid, pidx)], len 1 o 2
    km: int = 0
    value: int = 0

    def recompute(self, ctx: Escenario) -> None:
        """Recalcula km y valor del viaje con el mejor orden si hay 2 paradas."""
        cx, cy = ctx.center_xy[self.truck]
        if len(self.items) == 1:
            gid, pidx = self.items[0]
            gx, gy = ctx.station_xy[gid]
            self.km = 2 * ctx.manhattan((cx,cy), (gx,gy))
            self.value = ctx.petition_value_today(gid, pidx)
            return
        # dos paradas: prueba ambos órdenes
        (g1, i1), (g2, i2) = self.items
        x1, y1 = ctx.station_xy[g1]; x2, y2 = ctx.station_xy[g2]
        a = ctx.manhattan((cx,cy),(x1,y1)) + ctx.manhattan((x1,y1),(x2,y2)) + ctx.manhattan((x2,y2),(cx,cy))
        b = ctx.manhattan((cx,cy),(x2,y2)) + ctx.manhattan((x2,y2),(x1,y1)) + ctx.manhattan((x1,y1),(cx,cy))
        self.km = a if a < b else b
        self.value = ctx.petition_value_today(g1, i1) + ctx.petition_value_today(g2, i2)
