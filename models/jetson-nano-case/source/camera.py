"""Tilting Raspberry Pi Camera v2 mount for the 10 mm deck grid.

The foot bolts to two grid points 30 mm apart (M3 x 8 into the deck
inserts). The camera plate hinges on an M3 x 16 bolt with a nyloc nut;
tighten it until the plate holds its angle. The camera looks along -Y.
"""
import cadquery as cq
from params import *

EAR_GAP = 6.4                   # tongue 6.0 + clearance
EAR_T = 4.0
HINGE_Y = -8.0                  # in the foot frame
HINGE_Z = 11.0
FOOT_T = 5.0

PLATE_W = 29.0
PLATE_T = 3.0
PLATE_Z0 = 9.0                  # clears the ears (axis + 4) at any tilt
PLATE_Z1 = 40.0
CAM_Z0 = 13.0                   # camera board bottom edge in the plate frame
STANDOFF = 3.0
TONGUE_W = 6.0
TONGUE_AXIS = (7.0, 4.0)        # (y, z) of the hinge in the plate frame


def foot():
    f = (cq.Workplane("XY").center(0, -1).rect(40, 22).extrude(FOOT_T)
         .edges("|Z").fillet(3))
    for sx in (-1, 1):
        x = sx * (EAR_GAP / 2 + EAR_T / 2)
        ear = (cq.Workplane("YZ").workplane(offset=x - EAR_T / 2)
               .center(HINGE_Y, 0).rect(8, 2 * HINGE_Z, centered=(True, False))
               .extrude(EAR_T))
        ear = ear.union(cq.Workplane("YZ").workplane(offset=x - EAR_T / 2)
                        .center(HINGE_Y, HINGE_Z).circle(4).extrude(EAR_T))
        ear = ear.intersect(cq.Workplane("XY").rect(60, 60)
                            .extrude(HINGE_Z + 4))
        f = f.union(ear)
    hinge = (cq.Workplane("YZ").workplane(offset=-20).center(HINGE_Y, HINGE_Z)
             .circle(M3_CLEAR / 2).extrude(40))
    f = f.cut(hinge)
    # grid screws at (+-15, +4), 30 mm apart: clearance + counterbore, 3 mm under the head
    pts = [(-15, 4), (15, 4)]
    f = f.cut(cq.Workplane("XY").pushPoints(pts).circle(M3_CLEAR / 2)
              .extrude(FOOT_T))
    f = f.cut(cq.Workplane("XY").workplane(offset=3.0).pushPoints(pts)
              .circle(M3_HEAD / 2).extrude(FOOT_T))
    return f


def plate():
    p = (cq.Workplane("XZ").workplane(offset=-PLATE_T)
         .center(0, (PLATE_Z0 + PLATE_Z1) / 2)
         .rect(PLATE_W, PLATE_Z1 - PLATE_Z0).extrude(PLATE_T)
         .edges("|Y").fillet(3))
    ty, tz = TONGUE_AXIS
    tongue = (cq.Workplane("YZ").workplane(offset=-TONGUE_W / 2)
              .center((PLATE_T + ty + 4) / 2, tz + 4)
              .rect(ty + 4 - PLATE_T + 1, 8).extrude(TONGUE_W)
              .translate((0, -0.5, 0)))
    tongue = tongue.union(cq.Workplane("YZ").workplane(offset=-TONGUE_W / 2)
                          .center(ty, tz).circle(4).extrude(TONGUE_W))
    # brace from the tongue up the back of the plate
    brace = (cq.Workplane("YZ").workplane(offset=-TONGUE_W / 2)
             .polyline([(PLATE_T, tz), (ty + 4, tz), (PLATE_T, tz + 18)])
             .close().extrude(TONGUE_W))
    p = p.union(tongue).union(brace)
    p = p.cut(cq.Workplane("YZ").workplane(offset=-10).center(ty, tz)
              .circle(M3_CLEAR / 2).extrude(20))

    # camera standoffs on the front face (-Y), M2 self-tapping
    pts = [(sx * CAM_HOLES_X / 2, CAM_Z0 + z)
           for sx in (-1, 1) for z in CAM_HOLE_Z]
    st = (cq.Workplane("XZ").pushPoints(pts).circle(2.25).extrude(STANDOFF))
    p = p.union(st)
    p = p.cut(cq.Workplane("XZ").workplane(offset=-PLATE_T)
              .pushPoints(pts).circle(M2_PILOT / 2)
              .extrude(PLATE_T + STANDOFF))
    return p


def assembled(tilt=-15.0):
    """Foot and plate in the foot frame, plate tilted (negative = look down)."""
    ty, tz = TONGUE_AXIS
    pl = (plate().translate((0, -ty, -tz))
          .rotate((0, 0, 0), (1, 0, 0), tilt)
          .translate((0, HINGE_Y, HINGE_Z)))
    return foot(), pl
