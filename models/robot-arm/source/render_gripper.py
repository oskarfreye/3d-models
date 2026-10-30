"""Close-up render of the gripper module in its own frame.

The jaw, crank and rod are posed from the slider-crank solution, so the
image shows the real linkage at a representative opening instead of the
open end stop.

Run:  .venv/bin/python models/robot-arm/source/render_gripper.py
"""
import math
import os
import cadquery as cq
from cadquery import Assembly, Color

from gripper import body, jaw, crank, rod, SERVO_Z, CRANK_R, ROD_L
from servo import servo_body
from render import render

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "images")
os.makedirs(OUT, exist_ok=True)

GRIP_PHI = 60.0          # crank angle from the open end stop, degrees

YEL = Color(0.95, 0.74, 0.1)
BLU = Color(0.16, 0.42, 0.78)
GRY = Color(0.72, 0.74, 0.78)
BLK = Color(0.12, 0.12, 0.14)


def pose(phi=GRIP_PHI):
    """Return jaw translation and crank/rod rotations for a crank angle.

    The crank axis is at (0, SERVO_Z), the jaw pin runs on Z = SERVO_Z.
    phi = 0 is the open end stop, phi = 180 the closed one.
    """
    a = math.radians(phi)
    xp = -CRANK_R * math.cos(a)
    zp = SERVO_Z + CRANK_R * math.sin(a)
    dz = zp - SERVO_Z
    xj = xp - math.sqrt(ROD_L ** 2 - dz ** 2)
    mid = ((xp + xj) / 2.0, SERVO_Z + dz / 2.0)
    beta = math.atan2(-(SERVO_Z - zp), xj - xp)
    return xj, phi, mid, math.degrees(beta)


def gripper(phi=GRIP_PHI):
    xj, alpha, mid, beta = pose(phi)
    a = Assembly()
    a.add(body().val(), name="body", color=YEL)
    a.add(servo_body().rotate((0, 0, 0), (1, 1, 1), -120)
          .translate((0, 0, SERVO_Z)).val(), name="servo", color=BLK)
    a.add(jaw().translate((xj, 0, 0)).val(), name="jaw", color=BLU)
    a.add(crank().rotate((0, 0, 0), (1, 1, 1), -120)
          .translate((0, 0, SERVO_Z))
          .rotate((0, 0, SERVO_Z), (0, 1, SERVO_Z), 180)
          .rotate(cq.Vector(0, 0, SERVO_Z), cq.Vector(0, 1, SERVO_Z),
                  alpha).val(), name="crank", color=GRY)
    a.add(rod().rotate(cq.Vector(0, 0, SERVO_Z), cq.Vector(0, 1, SERVO_Z), beta)
          .translate((mid[0], 0, mid[1] - SERVO_Z)).val(),
          name="rod", color=GRY)
    return a


if __name__ == "__main__":
    a = gripper()
    render(a, os.path.join(OUT, "gripper.png"),
           direction=(0.55, 1.0, 0.22), width=900, height=780,
           fov=30, pad=1.22)
    print("render done")
