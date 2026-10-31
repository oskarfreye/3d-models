"""Interference checks between the parts and a rough board proxy.

Run:  .venv/bin/python models/jetson-nano-case/source/check_fit.py
"""
from antenna import holder
from camera import assembled
from case import base, lid
from render_all import board_proxy


def overlap(a, b):
    return a.intersect(b).val().Volume()


def main():
    b, l, h, bp = base(), lid(), holder(), board_proxy()
    s = h.val()
    bb = s.BoundingBox()
    print("holder bbox x[%.1f, %.1f] y[%.1f, %.1f] z[%.1f, %.1f], valid %s"
          % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax,
             s.isValid()))
    checks = [
        ("base / board", overlap(b, bp)),
        ("lid / board", overlap(l, bp)),
        ("base / lid", overlap(b, l)),
        ("holder / lid", overlap(h, l)),
    ]
    for tilt in (-60, -15, 0, 40):
        f, p = assembled(tilt)
        checks.append(("camera foot / plate at %d deg" % tilt, overlap(f, p)))
    for name, v in checks:
        print("%-32s %.3f mm3  %s" % (name, v, "ok" if v < 1e-3 else "CLASH"))
    assert all(v < 1e-3 for _, v in checks)


if __name__ == "__main__":
    main()
