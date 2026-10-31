"""Render the README images into ../images.

The board is a rough proxy (PCB, heatsink, I/O blocks), only for
checking the layout visually, not for fit decisions.
"""
import os
import cadquery as cq

from case import base, lid
from camera import assembled
from params import *
from render import render

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "images")


def board_proxy():
    pcb = (cq.Workplane("XY").workplane(offset=PCB_Z)
           .rect(BOARD_X, BOARD_Y).extrude(PCB_T))
    sink = (cq.Workplane("XY").workplane(offset=PCB_TOP)
            .center(-12, -5).rect(55, 60).extrude(26))
    io = cq.Workplane("XY")
    # barrel, HDMI+DP, USB stacks, RJ45, micro-USB along the +X edge
    for y0, y1, h in ((-48, -40, 11), (-35, -5, 7), (-3, 30, 16),
                      (32, 47, 13.5)):
        io = io.union(cq.Workplane("XY").workplane(offset=PCB_TOP)
                      .center(BOARD_X / 2 - 7, (y0 + y1) / 2)
                      .rect(16, y1 - y0).extrude(h))
    return pcb.union(sink).union(io)


def main():
    os.makedirs(IMG, exist_ok=True)
    b, l = base(), lid()
    f, p = assembled(-15)
    cam_at = (0, -59, TOP_Z)        # screws in the front deck row, y = -55

    a = cq.Assembly()
    a.add((b).val(), color=cq.Color(0.20, 0.22, 0.25))
    a.add((l).val(), color=cq.Color(0.85, 0.45, 0.10))
    a.add((f.translate(cam_at)).val(), color=cq.Color(0.20, 0.22, 0.25))
    a.add((p.translate(cam_at)).val(), color=cq.Color(0.85, 0.45, 0.10))
    render(a, os.path.join(IMG, "case.png"), (0.9, -1.0, 0.6),
           width=1000, height=800)

    open_a = cq.Assembly()
    open_a.add((b).val(), color=cq.Color(0.20, 0.22, 0.25))
    open_a.add((board_proxy()).val(), color=cq.Color(0.15, 0.55, 0.30))
    render(open_a, os.path.join(IMG, "base_board.png"), (1.0, -0.7, 0.9),
           width=1000, height=800)

    render(b.rotate((0, 0, 0), (1, 0, 0), 180),
           os.path.join(IMG, "underside.png"), (0.5, -0.8, 1.0),
           width=900, height=800)
    print("ok")


if __name__ == "__main__":
    main()
