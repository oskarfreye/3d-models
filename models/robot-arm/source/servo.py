"""Reusable ST3215 joint hardware.

Local frame: +Z is the servo output axis, the case front is Z=0,
the output axis is at X=0/Y=0. The case extends to +X.
"""
import math
import cadquery as cq
from params import *

# derived joint stack (with running clearance)
ADAPTER_LIFT = 0.6
SPIGOT_TOP = PLATE_T + ADAPTER_LIFT            # 5.6
ADAPTER_TOP_Z = SPIGOT_TOP + ADAPTER_FLANGE_T  # 12.6


def servo_body():
    """Simplified ST3215 solid, for assembly checks and renders."""
    body = (cq.Workplane("XY")
            .box(SERVO_L, SERVO_W, SERVO_BODY_H + SERVO_CAP_REAR)
            .translate((SERVO_L / 2 - AXIS_FROM_END, 0,
                        -(SERVO_BODY_H + SERVO_CAP_REAR) / 2)))
    horn = (cq.Workplane("XY").circle(HORN_D / 2)
            .extrude(SERVO_CAP_OUT))
    hub = (cq.Workplane("XY").circle(4.2).extrude(SERVO_CAP_OUT + 1.2))
    return body.union(horn).union(hub)


def horn_adapter(flange_d=None, inserts=None):
    """Bolts onto the 19.2 mm horn, presents a 4 x M3 insert face."""
    flange_d = flange_d or ADAPTER_FLANGE_D
    if inserts is None:
        inserts = [((M3_BCD / 2), 0), (0, (M3_BCD / 2)),
                   (-(M3_BCD / 2), 0), (0, -(M3_BCD / 2))]
    spigot = (cq.Workplane("XY").workplane(offset=HORN_TOP)
              .circle(ADAPTER_SPIGOT / 2).extrude(SPIGOT_TOP - HORN_TOP))
    flange = (cq.Workplane("XY").workplane(offset=SPIGOT_TOP)
              .circle(flange_d / 2).extrude(ADAPTER_FLANGE_T))
    p = spigot.union(flange)
    p = p.edges(">Z").chamfer(1.0)
    p = p.edges("%CIRCLE and <Z").chamfer(0.6)

    # clearance for the raised spline boss
    p = p.cut(cq.Workplane("XY").workplane(offset=HORN_TOP)
              .circle(4.7).extrude(1.4))
    # 8 x M2 horn screws, every 45 deg so either horn pattern works
    pts = [(HORN_BCD / 2 * math.cos(a), HORN_BCD / 2 * math.sin(a))
           for a in [i * 45 for i in range(8)]]
    p = (p.faces(">Z").workplane()
         .pushPoints(pts).cskHole(M2_CLEAR, 4.4, 90))
    # 4 x M3 heat-set inserts on a 26 mm bolt circle
    if inserts:
        p = (p.faces(">Z").workplane(origin=(0, 0, ADAPTER_TOP_Z))
             .pushPoints(inserts).hole(M3_INSERT_D, M3_INSERT_H))
    return p


def tool_adapter():
    """Wide horn adapter for the J5 tool face (4 x M3 at +/-18, +/-18)."""
    return horn_adapter(flange_d=56.0,
                        inserts=[(18, 18), (-18, 18), (-18, -18), (18, -18)])


def child_flange():
    """Proximal face of every moving link; bolts to a horn adapter."""
    p = (cq.Workplane("XY").box(CHILD_FLANGE_W, CHILD_FLANGE_W, CHILD_FLANGE_T)
         .translate((0, 0, CHILD_FLANGE_T / 2))
         .edges("|Z").fillet(4))
    pts = [(M3_BCD / 2, 0), (0, M3_BCD / 2),
           (-M3_BCD / 2, 0), (0, -M3_BCD / 2)]
    p = (p.faces(">Z").workplane()
         .pushPoints(pts).hole(M3_CLEAR))
    # cable pass-through / weight relief
    p = (p.faces(">Z").workplane()
         .circle(6).hole(12))
    p = p.faces(">Z").edges().chamfer(0.8)
    return p


def servo_pocket():
    """Servo shell with the 4 x M2 face plate. Parent side of a joint.

    Open at the back (Z-) for insertion, output at Z+.
    """
    outer = (cq.Workplane("XY").box(53, 33, 36.5)
             .translate((12.5, 0, -18.25))
             .edges("|Z").fillet(3.5))
    inner = (cq.Workplane("XY").box(46.8, 26.6, 36.6)
             .translate((12.5, 0, -18.3)))
    pocket = outer.cut(inner)

    plate = (cq.Workplane("XY").box(53, 33, PLATE_T)
             .translate((12.5, 0, PLATE_T / 2))
             .edges("|Z").fillet(3.5))
    p = pocket.union(plate)

    # horn clearance
    p = p.cut(cq.Workplane("XY").circle(PLATE_HOLE / 2).extrude(PLATE_T + 0.2))
    # 4 x M2 servo screws
    pts = [(x, y) for x in MOUNT_X for y in (MOUNT_Y, -MOUNT_Y)]
    p = (p.faces(">Z").workplane()
         .pushPoints(pts).cboreHole(M2_CLEAR, 4.3, 1.2))
    # cable window in the +Y wall, near the output
    p = p.cut(cq.Workplane("XY").box(18, 8, 10)
              .translate((1, 15.5, -20)))
    # soften insertion edges
    p = p.edges("%CIRCLE and <Z").chamfer(0.8)
    return p


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "..", "stl")
    os.makedirs(out, exist_ok=True)
    for name, shape in (("horn_adapter", horn_adapter()),
                        ("child_flange", child_flange()),
                        ("servo_pocket_test", servo_pocket())):
        cq.exporters.export(shape, os.path.join(out, name + ".stl"))
        bb = shape.val().BoundingBox()
        print("%-18s %6.1f x %6.1f x %6.1f mm" %
              (name, bb.xlen, bb.ylen, bb.zlen))
