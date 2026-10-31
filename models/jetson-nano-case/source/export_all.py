"""Export every printable part and assert it fits the Bambu Lab A1 mini.

Run:  .venv/bin/python models/jetson-nano-case/source/export_all.py
"""
import os
import cadquery as cq

from case import base, lid, fit_test
from camera import foot, plate
from params import BED, TOP_Z, SPLIT_Z

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "stl")


def lid_print():
    """Lid flipped roof-down for printing."""
    return lid().rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, TOP_Z))


def plate_print():
    """Camera plate on its side, hinge axis vertical."""
    return plate().rotate((0, 0, 0), (0, 1, 0), 90)


PARTS = [
    ("base", base),
    ("lid", lid_print),
    ("camera_foot", foot),
    ("camera_plate", plate_print),
    ("fit_test", fit_test),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    bad = []
    for name, make in PARTS:
        shape = make()
        s = shape.val()
        assert s.isValid(), name
        bb = s.BoundingBox()
        dims = (bb.xlen, bb.ylen, bb.zlen)
        fits = all(d <= BED for d in dims)
        cq.exporters.export(shape, os.path.join(OUT, name + ".stl"),
                            tolerance=0.02, angularTolerance=0.1)
        print("%-14s %6.1f x %6.1f x %6.1f  %4.0f g PETG solid  %s"
              % (name, *dims, s.Volume() / 1000 * 1.27,
                 "ok" if fits else "TOO BIG"))
        if not fits:
            bad.append(name)
    assert not bad, bad


if __name__ == "__main__":
    main()
