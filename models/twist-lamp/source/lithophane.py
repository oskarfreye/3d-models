#!/usr/bin/env python3
"""Cylindrical lithophane shade for the Twist Lamp base.

The shade slides over the base collar like schirm.stl. The inside is a smooth
cylinder; the photo is on the outside: dark pixels are thick, light pixels thin.

    python3 lithophane.py photo.jpg -o ../stl/schirm_lithophane.stl

The photo wraps once around the shade (360°, the seam is at the back of the
image edges). Image area is about 273 x 139 mm, so a photo with a ~2:1 aspect
ratio fills it without stretching. Use --fit to letterbox instead of cropping.
"""
import argparse
import math
import struct

import numpy as np
from PIL import Image, ImageOps

# Must match source/lampe.scad
KRAGEN_R = 43.3  # collar radius at the bottom
KRAGEN_H = 6.0


def load_heights(path, cols, rows, fit, invert, gamma):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img).convert("L")
    if fit:
        img = ImageOps.pad(img, (cols, rows), color=255)  # white = thin border
    else:
        img = ImageOps.fit(img, (cols, rows), method=Image.LANCZOS)
    a = np.asarray(img, dtype=np.float64) / 255.0
    if invert:
        a = 1.0 - a
    return a ** gamma  # brightness 0..1, row 0 = top


def build(args):
    r_in = args.innen_r
    circ = 2 * math.pi * r_in
    img_h = args.hoehe - args.rand_unten - args.rand_oben
    cols = int(round(circ / args.aufloesung))
    rows = int(round(img_h / args.aufloesung))

    bright = load_heights(args.bild, cols, rows, args.fit, args.invert, args.gamma)
    thick = args.min_dicke + (1.0 - bright) * (args.max_dicke - args.min_dicke)
    thick = thick[::-1]  # row 0 = bottom

    theta = 2 * math.pi * (np.arange(cols) + 0.5) / cols
    ct, st = np.cos(theta), np.sin(theta)

    # Outer surface rows: (z, radius per column)
    band = np.full(cols, r_in + args.rand_dicke)
    z_img = args.rand_unten + (np.arange(rows) + 0.5) * img_h / rows
    outer = [(0.0, band), (args.rand_unten, band)]
    outer += [(args.rand_unten, r_in + thick[0])]
    outer += [(z, r_in + thick[j]) for j, z in enumerate(z_img)]
    top = args.hoehe - args.rand_oben
    outer += [(top, r_in + thick[-1]), (top, band), (args.hoehe, band)]

    nr = len(outer)
    verts = np.empty((nr * cols + 2 * cols, 3))
    for j, (z, r) in enumerate(outer):
        s = slice(j * cols, (j + 1) * cols)
        verts[s, 0], verts[s, 1], verts[s, 2] = r * ct, r * st, z
    ib, it = nr * cols, nr * cols + cols  # inner bottom / top rings
    verts[ib:ib + cols] = np.c_[r_in * ct, r_in * st, np.zeros(cols)]
    verts[it:it + cols] = np.c_[r_in * ct, r_in * st, np.full(cols, args.hoehe)]

    i = np.arange(cols)
    i2 = (i + 1) % cols
    tris = []
    # Outer wall, normals outward
    for j in range(nr - 1):
        a, b = j * cols + i, j * cols + i2
        c, d = a + cols, b + cols
        tris += [np.c_[a, b, d], np.c_[a, d, c]]
    # Inner wall, normals inward
    tris += [np.c_[ib + i, it + i, it + i2], np.c_[ib + i, it + i2, ib + i2]]
    # Bottom ring (normals down) and top ring (normals up)
    o0, oN = i, (nr - 1) * cols + i
    o0b, oNb = i2, (nr - 1) * cols + i2
    tris += [np.c_[o0, ib + i, ib + i2], np.c_[o0, ib + i2, o0b]]
    tris += [np.c_[oN, oNb, it + i2], np.c_[oN, it + i2, it + i]]
    faces = np.vstack(tris)
    return verts, faces, bright, (cols, rows, img_h)


def write_stl(path, verts, faces):
    tri = verts[faces]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    rec = np.zeros(len(faces), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = n, tri
    with open(path, "wb") as f:
        f.write(b"Twist Lamp lithophane".ljust(80, b" "))
        f.write(struct.pack("<I", len(faces)))
        f.write(rec.tobytes())


def preview(path, bright, args):
    """Rough backlit preview: light through the wall falls off with thickness."""
    t = args.min_dicke + (1.0 - bright) * (args.max_dicke - args.min_dicke)
    light = np.exp(-0.9 * (t - args.min_dicke))
    Image.fromarray((255 * light / light.max()).astype(np.uint8)).save(path)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("bild", help="photo (jpg/png)")
    p.add_argument("-o", "--out", default="schirm_lithophane.stl")
    p.add_argument("--vorschau", help="also save a simulated backlit PNG")
    p.add_argument("--hoehe", type=float, default=150.0, help="shade height (mm)")
    p.add_argument("--innen_r", type=float, default=KRAGEN_R + 0.15, help="inner radius (mm)")
    p.add_argument("--min_dicke", type=float, default=0.8, help="wall at white pixels (mm)")
    p.add_argument("--max_dicke", type=float, default=3.0, help="wall at black pixels (mm)")
    p.add_argument("--rand_unten", type=float, default=KRAGEN_H + 3, help="plain band over the collar (mm)")
    p.add_argument("--rand_oben", type=float, default=3.0, help="plain band at the top (mm)")
    p.add_argument("--rand_dicke", type=float, default=2.0, help="wall of the plain bands (mm)")
    p.add_argument("--aufloesung", type=float, default=0.3, help="mm per pixel")
    p.add_argument("--gamma", type=float, default=1.0)
    p.add_argument("--fit", action="store_true", help="letterbox instead of crop")
    p.add_argument("--invert", action="store_true")
    args = p.parse_args()

    verts, faces, bright, (cols, rows, img_h) = build(args)
    write_stl(args.out, verts, faces)
    if args.vorschau:
        preview(args.vorschau, bright, args)
    print(f"{args.out}: {len(faces)} triangles, image {cols}x{rows} px "
          f"= {2*math.pi*args.innen_r:.0f} x {img_h:.0f} mm, ideal aspect {2*math.pi*args.innen_r/img_h:.2f}:1")


if __name__ == "__main__":
    main()
