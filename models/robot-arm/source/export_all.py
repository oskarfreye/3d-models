"""Export every printable part and assert it fits the Bambu Lab A1 mini.

Run:  .venv/bin/python models/robot-arm/source/export_all.py
"""
import os
import cadquery as cq

from servo import horn_adapter, tool_adapter, child_flange, servo_pocket
from links import turret, link, wrist
from base import base, base_lid, camera_mast
from gripper import body as gripper_body, jaw as gripper_jaw
from gripper import crank as gripper_crank, rod as gripper_rod
from params import UPPER_ARM, FOREARM

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "stl")
BED = 180.0

PARTS = [
    ("base", base()),
    ("base_lid", base_lid()),
    ("camera_mast", camera_mast()),
    ("turret", turret()),
    ("upper_arm", link(UPPER_ARM)),
    ("forearm", link(FOREARM)),
    ("wrist", wrist()),
    ("horn_adapter", horn_adapter()),
    ("tool_adapter", tool_adapter()),
    ("child_flange", child_flange()),
    ("servo_pocket_test", servo_pocket()),
    ("gripper_body", gripper_body()),
    ("gripper_jaw", gripper_jaw()),
    ("gripper_crank", gripper_crank()),
    ("gripper_rod", gripper_rod()),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    bad = []
    total = 0.0
    for name, shape in PARTS:
        bb = shape.val().BoundingBox()
        dims = (bb.xlen, bb.ylen, bb.zlen)
        total += shape.val().Volume() / 1000.0
        fits = all(d <= BED for d in dims)
        cq.exporters.export(shape, os.path.join(OUT, name + ".stl"))
        print("%-18s %6.1f x %6.1f x %6.1f  %5.0f g  %s"
              % (name, dims[0], dims[1], dims[2],
                 shape.val().Volume() / 1000.0 * 1.27,
                 "OK" if fits else "TOO BIG"))
        if not fits:
            bad.append((name, dims))
    print("-" * 64)
    print("parts: %d   filament (PETG, solid): %.0f g" % (len(PARTS), total * 1.27))
    if bad:
        raise SystemExit("oversize parts: %r" % (bad,))
    print("all parts fit the 180 x 180 x 180 mm bed")


if __name__ == "__main__":
    main()
