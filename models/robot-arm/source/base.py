"""Base with the J1 servo bay, electronics tray and camera mast."""
import math
import cadquery as cq
from params import *
from servo import servo_pocket

WALL = 3.5
TOP_T = 4.0
BOT_T = 5.0
TOP_Z = BASE_H
INNER = BASE_W - 2 * WALL          # 143
LID = INNER - 0.4                  # clearance
BOSS_XY = 66.5


def base():
    # outer shell, open at the bottom for the electronics tray
    shell = (cq.Workplane("XY").box(BASE_W, BASE_D, BASE_H)
             .translate((0, 0, BASE_H / 2))
             .edges("|Z").fillet(10))
    inner = (cq.Workplane("XY").box(INNER, INNER, BASE_H + 1)
             .translate((0, 0, BASE_H / 2)))
    p = shell.cut(inner)

    # top plate, with the J1 pocket opening
    top = (cq.Workplane("XY").box(BASE_W, BASE_D, TOP_T)
           .translate((0, 0, BASE_H - TOP_T / 2))
           .edges("|Z").fillet(10))
    # J1 opening: match the servo pocket cavity (which is offset +12.5 in X
    # because the servo axis sits 10.11 mm from the case end)
    top = top.cut(cq.Workplane("XY").box(47, 26.8, TOP_T + 2)
                  .translate((12.5, 0, BASE_H - TOP_T / 2)))
    p = p.union(top)

    # J1 servo pocket, output up
    p = p.union(servo_pocket().translate((0, 0, BASE_H)))

    # corner bosses for the bottom tray, fused to the side walls
    for sx in (-1, 1):
        for sy in (-1, 1):
            b = (cq.Workplane("XY").circle(6).extrude(12)
                 .translate((sx * BOSS_XY, sy * BOSS_XY, 5)))
            b = b.cut(cq.Workplane("XY").circle(M3_INSERT_D / 2)
                      .extrude(8).translate((sx * BOSS_XY, sy * BOSS_XY, 5)))
            p = p.union(b)

    # cable slot in the back wall
    p = p.cut(cq.Workplane("XY").box(34, 20, 14)
              .translate((0, -BASE_D / 2, 30)))

    # camera mast socket at the back: foot recess + post clearance
    p = p.union(cq.Workplane("XY").box(30, 30, 26)
                .translate((0, -56, BASE_H + 13)))
    p = p.cut(cq.Workplane("XY").box(26.6, 26.6, 6.2)
              .translate((0, -56, BASE_H + 22.9)))
    p = p.cut(cq.Workplane("XY").box(18.6, 18.6, 22)
              .translate((0, -56, BASE_H + 10)))

    # electronics mounting grid on the floor (M3 inserts from the top)
    # (handled by the standoffs on the removable lid)
    return p


def base_lid():
    p = (cq.Workplane("XY").box(LID, LID, BOT_T)
         .translate((0, 0, BOT_T / 2)).edges("|Z").fillet(6.5))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = p.cut(cq.Workplane("XY").circle(M3_CLEAR).extrude(BOT_T + 1)
                      .translate((sx * BOSS_XY, sy * BOSS_XY, -1)))
            # countersink the screw heads from below
            p = p.cut(cq.Workplane("XY").circle(M3_HEAD / 2 + 0.2)
                      .extrude(2.2).translate((sx * BOSS_XY, sy * BOSS_XY,
                                               -0.5)))
    # rubber feet recesses
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = p.cut(cq.Workplane("XY").circle(8).extrude(1.2)
                      .translate((sx * 52, sy * 52, -0.1)))
    # vent slots
    for i in range(5):
        p = p.cut(cq.Workplane("XY").box(4, 26, BOT_T + 1)
                  .translate((-40 + i * 20, 58, BOT_T / 2)))

    # electronics standoffs (Pico + driver board), 4 x M3 inserts
    for x in (-24, 24):
        for y in (-16, 16):
            b = (cq.Workplane("XY").circle(5.5).extrude(6)
                 .translate((x, y - 20, BOT_T)))
            b = b.cut(cq.Workplane("XY").circle(M3_INSERT_D / 2).extrude(6.2)
                      .translate((x, y - 20, BOT_T)))
            p = p.union(b)
    return p


def camera_mast():
    """Slotted post with a tilted C270 cradle, fits the A1 mini upright."""
    post_h = 122.0
    p = (cq.Workplane("XY").box(18, 18, post_h)
         .translate((0, 0, post_h / 2)).edges("|Z").fillet(2))
    p = p.union(cq.Workplane("XY").box(26, 26, 6)
                .translate((0, 0, 3)).edges("|Z").fillet(3))

    # tilted head plate
    head = (cq.Workplane("XY").box(56, 46, 5)
            .translate((0, 0, 2.5)))
    head = head.rotate((0, 0, 0), (1, 0, 0), -25)
    head = head.translate((0, 12, post_h + 2))
    p = p.union(head)

    # lip and strap slots
    lip = (cq.Workplane("XY").box(56, 4, 18)
           .translate((0, -20, post_h + 7)))
    p = p.union(lip)
    for x in (-22, 22):
        p = p.cut(cq.Workplane("XY").box(5, 30, 5)
                  .translate((x, 8, post_h + 4)))
    return p


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "..", "stl")
    os.makedirs(out, exist_ok=True)
    for name, shape in (("base", base()), ("base_lid", base_lid()),
                        ("camera_mast", camera_mast())):
        cq.exporters.export(shape, os.path.join(out, name + ".stl"))
        bb = shape.val().BoundingBox()
        print("%-14s %6.1f x %6.1f x %6.1f" % (name, bb.xlen, bb.ylen, bb.zlen))
