"""Single-moving-jaw gripper driven by the 6th ST3215.

Local frame: tool face at Z=0, +Z forward, jaws close along X.
The servo lies across the body with its output axis +Y; the crank and
connecting rod work on the front face at Y > 0.

The moving jaw slides on two M3 screws that thread into heat-set inserts
behind the front plate. The crank drives it through a 30 mm connecting
rod. Grip range approx. 12 ... 40 mm, enough for 40 mm table tennis balls.
"""
import math
import cadquery as cq
from params import *
from servo import horn_adapter, ADAPTER_TOP_Z

# --- tool interface --------------------------------------------------------
TOOL_W = 52.0
TOOL_T = 6.0
TOOL_BCD = 18.0                # 4 x M3 at (+/-18, +/-18)

# --- servo -----------------------------------------------------------------
SERVO_Z = 30.0                 # output axis height above the tool face
FRONT_T = 5.0                  # servo mounting plate
HOUSING_X = 16.0
HOUSING_Y0 = -38.0
HOUSING_Z0 = 6.0
HOUSING_Z1 = 70.0

# --- front plate / jaw guide ----------------------------------------------
PLATE_X0 = -32.0
PLATE_X1 = 16.0
PLATE_Z0 = 16.0
PLATE_Z1 = 66.0
GUIDE_X = -26.5                # fixed guide screws, jaw mid position
GUIDE_Z = (20.0, 54.0)         # upper screw above the crank-boss sweep
GUIDE_SLOT_L = 38.0

# --- jaw / rod planes ------------------------------------------------------
JAW_Y0 = 13.0                  # clears the crank flange (ends at 12.6)
JAW_T = 6.0
ROD_Y0 = 25.0
ROD_T = 5.0

# --- crank / rod -----------------------------------------------------------
CRANK_R = 14.0
ROD_L = 30.0
JAW_MID = -26.5                # jaw pin X at mid stroke
PAD_FIXED = 26.0               # fixed pad face X
PAD_LOCAL = 30.0               # moving pad face, jaw-local


def cyl_y(x, z, d, y0, y1):
    """Cylinder along Y between y0 and y1 (y1 > y0)."""
    return (cq.Workplane("XZ").center(x, z).circle(d / 2)
            .extrude(y1 - y0).translate((0, y1, 0)))


def body():
    # tool plate
    p = (cq.Workplane("XY").box(TOOL_W, TOOL_W, TOOL_T)
         .translate((0, 0, TOOL_T / 2)).edges("|Z").fillet(4))
    for x in (-TOOL_BCD, TOOL_BCD):
        for y in (-TOOL_BCD, TOOL_BCD):
            p = p.cut(cq.Workplane("XY").circle(M3_CLEAR)
                      .extrude(TOOL_T + 2).translate((x, y, -1)))
    p = p.cut(cq.Workplane("XY").circle(9).extrude(TOOL_T + 2)
              .translate((0, 0, -1)))

    # servo housing, open at the back (-Y) for insertion
    house = (cq.Workplane("XY")
             .box(2 * HOUSING_X, -HOUSING_Y0, HOUSING_Z1 - HOUSING_Z0)
             .translate((0, HOUSING_Y0 / 2,
                         (HOUSING_Z0 + HOUSING_Z1) / 2))
             .edges("|Y").fillet(4))
    # cavity open to the bottom so the 4 M2 horn screws stay reachable
    # through the Ø18 access hole in the tool plate
    house = house.cut(cq.Workplane("XY").box(26.0, 42, 60)
                      .translate((0, -21, 36.5)))
    # cable slot at the back
    house = house.cut(cq.Workplane("XY").box(20, 8, 8)
                      .translate((0, HOUSING_Y0 + 1, 58)))
    p = p.union(house)

    # front plate: servo screws, horn opening, jaw guide inserts
    plate = (cq.Workplane("XY")
             .box(PLATE_X1 - PLATE_X0, FRONT_T, PLATE_Z1 - PLATE_Z0)
             .translate(((PLATE_X0 + PLATE_X1) / 2, FRONT_T / 2,
                         (PLATE_Z0 + PLATE_Z1) / 2))
             .edges("|Y").fillet(4))
    plate = plate.cut(cq.Workplane("XY").circle(PLATE_HOLE / 2)
                      .extrude(FRONT_T + 2).translate((0, -1, SERVO_Z)))
    # 4 x M2 servo screws, countersunk from the front
    for x in (-MOUNT_Y, MOUNT_Y):
        for z in (SERVO_Z + MOUNT_X[0], SERVO_Z + MOUNT_X[1]):
            plate = plate.cut(cq.Workplane("XY").circle(M2_CLEAR)
                              .extrude(FRONT_T + 2).translate((x, -1, z)))
            plate = plate.cut(cq.Workplane("XY").circle(4.3)
                              .extrude(1.6).translate((x, FRONT_T - 1.6, z)))
    # clearance for the jaw guide screws
    for z in GUIDE_Z:
        plate = plate.cut(cyl_y(GUIDE_X, z, M3_CLEAR, -1, FRONT_T + 1))
    p = p.union(plate)

    # guide posts: the jaw rides on their front faces (Y = JAW_Y0)
    for z in GUIDE_Z:
        post = cyl_y(GUIDE_X, z, 10.0, 0, JAW_Y0)
        post = post.cut(cyl_y(GUIDE_X, z, M3_CLEAR, -0.1, JAW_Y0 + 0.1))
        p = p.union(post)
        # heat-set insert pocket behind the plate
        b = (cq.Workplane("XY").box(11, 6.5, 11)
             .translate((GUIDE_X, -3.25, z)))
        b = b.cut(cyl_y(GUIDE_X, z, M3_INSERT_D, -6.6, 0.5))
        p = p.union(b)

    # fixed jaw: bridge under the grip zone plus a vertical pad
    p = p.union(cq.Workplane("XY").box(24, 20, 6)
                .translate((22, 10, 55)))
    p = p.union(cq.Workplane("XY").box(8, 14, 36)
                .translate((PAD_FIXED + 4, 20, 76)))
    # trim the pad top level with the moving finger, across its full width
    p = p.cut(cq.Workplane("XY").box(10, 16, 8)
              .translate((PAD_FIXED + 5, 20, 96)))
    return p


def jaw():
    """Moving jaw, drawn at mid stroke. Pin at the origin.

    The two long slots ride on the fixed guide screws; the finger reaches
    PAD_LOCAL forward of the pin.
    """
    p = (cq.Workplane("XY").box(46, JAW_T, 46)
         .translate((1, JAW_Y0 + JAW_T / 2, 39)).edges("|Y").fillet(3))
    # guide slots
    for z in GUIDE_Z:
        p = p.cut(cq.Workplane("XY").box(GUIDE_SLOT_L, JAW_T + 2, 3.6)
                  .translate((0, JAW_Y0 + JAW_T / 2, z)))
    # finger, pad face at local X = PAD_LOCAL
    p = p.union(cq.Workplane("XY").box(8, 17, 36)
                .translate((26, 21.5, 76)))
    # rib tying the finger back into the body
    p = p.union(cq.Workplane("XY").box(6, JAW_T, 34)
                .translate((24, JAW_Y0 + JAW_T / 2, 77)))
    # clearance for the crank boss through the whole stroke: the boss
    # intrudes into the jaw edge from Z = 32 up to Z = 49 at mid stroke
    p = p.cut(cq.Workplane("XY").box(11, JAW_T + 2, 18)
              .translate((21.5, JAW_Y0 + JAW_T / 2, 40.5)))
    p = p.cut(cq.Workplane("XY").box(12, 19, 6)
              .translate((26, 21.5, 95)))
    # pin boss for the connecting rod, tapped M3 from the front
    p = p.union(cyl_y(0, SERVO_Z, 10.0, JAW_Y0 + JAW_T, ROD_Y0))
    p = p.cut(cyl_y(0, SERVO_Z, 2.5, JAW_Y0 + JAW_T, ROD_Y0 + 0.1))
    return p


def crank():
    """Horn adapter with one crank pin at radius 14.

    The adapter is mounted in the servo frame; the pin at local +Y becomes
    +X in the gripper frame. The boss is long enough to reach the rod plane.
    """
    p = horn_adapter(inserts=[])
    boss = (cq.Workplane("XY").circle(5).extrude(ROD_Y0 - ADAPTER_TOP_Z)
            .translate((0, CRANK_R, ADAPTER_TOP_Z)))
    p = p.union(boss)
    # M3 pilot, tapped from the rod side
    p = p.cut(cq.Workplane("XY").circle(1.25)
              .extrude(ROD_Y0 - 18.5).translate((0, CRANK_R, 18.5)))
    return p


def rod():
    """Connecting rod, holes 30 mm apart, lying in the XZ plane."""
    p = (cq.Workplane("XY").box(ROD_L + 8, ROD_T, 10)
         .translate((0, ROD_Y0 + ROD_T / 2, SERVO_Z))
         .edges("|Y").fillet(2.5))
    for x in (-ROD_L / 2, ROD_L / 2):
        p = p.cut(cyl_y(x, SERVO_Z, 3.4, ROD_Y0 - 0.1, ROD_Y0 + ROD_T + 0.1))
    return p


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "..", "stl")
    os.makedirs(out, exist_ok=True)
    for name, shape in (("gripper_body", body()), ("gripper_jaw", jaw()),
                        ("gripper_crank", crank()), ("gripper_rod", rod())):
        cq.exporters.export(shape, os.path.join(out, name + ".stl"))
        bb = shape.val().BoundingBox()
        print("%-16s %6.1f x %6.1f x %6.1f" % (name, bb.xlen, bb.ylen, bb.zlen))
