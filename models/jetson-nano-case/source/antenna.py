"""Antenna holder for the top deck, with a cable canal down the back wall.

The RP-SMA bulkheads can't go in the lid's back wall from the inside:
the heatsink sits too close. Instead they mount vertically in this hood,
which screws onto two back-row deck inserts (X = -45, Y = +-35). The
pigtails run from the bulkheads to the back edge, down a canal on the
outside of the lid's back wall, and into the case through the two
existing antenna holes.

Coordinates are the case frame; the hood sits on the roof at TOP_Z.
"""
import cadquery as cq
from params import *

H = 20.0                        # hood height above the deck
T = 2.0                         # walls
TOP_T = 3.0                     # bulkhead panel, RP-SMA takes up to ~5
X0, X1 = -OUT_X / 2 - 5.0, -35.0    # overhangs the back edge by the canal
Y_HALF = 42.0
SCREWS = [(-45.0, -35.0), (-45.0, 35.0)]
SCREW_CBORE_H = 5.0             # pillar under the head: M3 x 10 into insert
PILLAR_R = 4.5
BULKHEADS = [(-42.0, -15.0), (-42.0, 15.0)]

CANAL_Z0 = ANT_Z - ANT_D / 2 - 3.0  # below the lower edge of the wall holes
CANAL_Y = 24.0                  # +-, covers the holes at Y = +-20
CANAL_DEPTH = 3.0


def holder():
    z0, z1 = TOP_Z, TOP_Z + H
    wall_x = -OUT_X / 2

    hood = (cq.Workplane("XY").workplane(offset=z0)
            .center((X0 + X1) / 2, 0).rect(X1 - X0, 2 * Y_HALF)
            .extrude(H).edges("|Z").fillet(3))
    leg = (cq.Workplane("XY").workplane(offset=CANAL_Z0)
           .center((X0 + wall_x) / 2, 0).rect(wall_x - X0, 2 * CANAL_Y + 2 * T)
           .extrude(z0 - CANAL_Z0))
    h = hood.union(leg)

    cavity = (cq.Workplane("XY").workplane(offset=z0 - 1)
              .center((X0 + T + X1 - T) / 2, 0)
              .rect(X1 - X0 - 2 * T, 2 * Y_HALF - 2 * T)
              .extrude(H - TOP_T + 1))
    canal = (cq.Workplane("XY").workplane(offset=CANAL_Z0 - 1)
             .center(wall_x - CANAL_DEPTH / 2, 0)
             .rect(CANAL_DEPTH, 2 * CANAL_Y).extrude(z0 - CANAL_Z0 + 2))
    h = h.cut(cavity).cut(canal)

    pillars = (cq.Workplane("XY").workplane(offset=z0).pushPoints(SCREWS)
               .circle(PILLAR_R).extrude(H))
    h = h.union(pillars)
    h = h.cut(cq.Workplane("XY").workplane(offset=z0 - 1).pushPoints(SCREWS)
              .circle(M3_CLEAR / 2).extrude(H + 2))
    h = h.cut(cq.Workplane("XY").workplane(offset=z0 + SCREW_CBORE_H)
              .pushPoints(SCREWS).circle(M3_HEAD / 2).extrude(H))

    h = h.cut(cq.Workplane("XY").workplane(offset=z1 - TOP_T - 1)
              .pushPoints(BULKHEADS).circle(ANT_D / 2).extrude(TOP_T + 2))
    return h
