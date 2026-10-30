"""Turret and arm links. Each link is one printable part.

Link frame: the proximal joint axis is at the origin, +Z runs along the
link, the joint axis is +Y. The servo pocket is at the distal end.
"""
import math
import cadquery as cq
from params import *
from servo import servo_pocket, ADAPTER_TOP_Z

PLATE_Y0 = ADAPTER_TOP_Z            # 12.6, proximal mounting face
PLATE_T = 6.0
PLATE_W = 36.0
PLATE_H = 56.0
POCKET_DEPTH = 39.0                 # pocket outer reaches this far back


def cyl_y(x, z, d, y0, y1):
    """Cylinder along Y between y0 and y1 (y1 > y0)."""
    h = y1 - y0
    c = (cq.Workplane("XZ").center(x, z).circle(d / 2).extrude(h))
    return c.translate((0, y1, 0))


def prox_plate(height=PLATE_H, width=PLATE_W):
    """Vertical fin bolted to the previous horn adapter."""
    p = (cq.Workplane("XY")
         .box(width, PLATE_T, height)
         .translate((0, PLATE_Y0 + PLATE_T / 2, 0))
         .edges("|Y").fillet(6))
    pts = [(M3_BCD / 2, 0), (0, M3_BCD / 2),
           (-M3_BCD / 2, 0), (0, -M3_BCD / 2)]
    for x, z in pts:
        p = p.cut(cyl_y(x, z, M3_CLEAR, PLATE_Y0, PLATE_Y0 + PLATE_T + 1))
        p = p.cut(cyl_y(x, z, 6.4, PLATE_Y0 + PLATE_T - 1.8,
                        PLATE_Y0 + PLATE_T + 1))
    p = p.cut(cyl_y(0, 0, 14, PLATE_Y0, PLATE_Y0 + PLATE_T + 1))
    return p


def orient_pocket(p):
    """Rotate the servo pocket so its axis is +Y and its body points -Z."""
    return (p.rotate((0, 0, 0), (0, 1, 0), 90)
             .rotate((0, 0, 0), (0, 0, 1), 90))


def link(length, beam_w=34):
    """Straight arm link: fin -> lofted beam -> servo pocket."""
    p = prox_plate()

    beam = (cq.Workplane("XY").workplane(offset=18)
            .center(0, 25.6).rect(beam_w, 26)
            .workplane(offset=(length - 36.0 - 18))
            .center(0, 0).rect(beam_w - 4, 26)
            .loft())
    p = p.union(beam)

    p = p.union(orient_pocket(servo_pocket()).translate((0, 0, length)))
    return p


def turret(rise=52.0):
    """J1 output -> J2 axis. Bolts to the J1 horn adapter."""
    p = (cq.Workplane("XY").box(40, 40, 6)
         .translate((0, 0, 3)).edges("|Z").fillet(4))
    pts = [(M3_BCD / 2, 0), (0, M3_BCD / 2),
           (-M3_BCD / 2, 0), (0, -M3_BCD / 2)]
    p = (p.faces(">Z").workplane().pushPoints(pts)
         .cboreHole(M3_CLEAR, 6.4, 1.6))
    p = (p.faces(">Z").workplane().circle(7).hole(14))

    col_h = rise - POCKET_DEPTH
    p = p.union(cq.Workplane("XY").box(44, 40, col_h)
                .translate((0, -4, 6 + col_h / 2)))
    p = p.union(cq.Workplane("XY").box(44, 44, 8)
                .translate((0, -4, 8 + col_h)))
    p = p.union(orient_pocket(servo_pocket()).translate((0, 0, rise)))
    return p


def wrist(j4_to_j5=58.0):
    """J4 pitch -> J5 roll. Roll axis 30 mm to +Y of the J4 axis.

    The J5 pocket opens downward so the servo can be inserted before the
    wrist is bolted to the J4 horn adapter. A side fin carries the load.
    """
    p = prox_plate(height=44)

    # side fin from the J4 plate up to the J5 pocket; stops 0.2 mm short
    # of the servo cavity so the servo still slides in from below
    fin = (cq.Workplane("XY").box(36, 3.9, 48)
           .translate((0, 14.55, 36)))
    p = p.union(fin)

    # J5 pocket, axis +Z, body toward -Z
    p = p.union(servo_pocket().translate((0, 30, j4_to_j5)))
    return p


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "..", "stl")
    os.makedirs(out, exist_ok=True)
    for name, shape in (("turret", turret()),
                        ("upper_arm", link(UPPER_ARM)),
                        ("forearm", link(FOREARM)),
                        ("wrist", wrist(WRIST_ROLL))):
        cq.exporters.export(shape, os.path.join(out, name + ".stl"))
        bb = shape.val().BoundingBox()
        print("%-12s %6.1f x %6.1f x %6.1f" % (name, bb.xlen, bb.ylen, bb.zlen))
