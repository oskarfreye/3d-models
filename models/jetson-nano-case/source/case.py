"""Base tray, lid and hole fit test for the Jetson Nano case."""
import cadquery as cq
from params import *

INNER_X = OUT_X - 2 * WALL
INNER_Y = OUT_Y - 2 * WALL
SKIP_NEAR_HOLE = 4.5            # no underside insert this close to a standoff


def _shell(z0, z1):
    """Rounded outer block minus the inner cavity, from z0 to z1."""
    outer = (cq.Workplane("XY").workplane(offset=z0)
             .rect(OUT_X, OUT_Y).extrude(z1 - z0)
             .edges("|Z").fillet(CORNER_R))
    inner = (cq.Workplane("XY").workplane(offset=z0)
             .rect(INNER_X, INNER_Y).extrude(z1 - z0)
             .edges("|Z").fillet(CORNER_R - WALL))
    return outer.cut(inner)


def _posts(z0, z1):
    return (cq.Workplane("XY").workplane(offset=z0)
            .pushPoints(POSTS).circle(POST_R).extrude(z1 - z0))


def _holes(points, d, z_top, depth):
    """Vertical holes going down from z_top."""
    return (cq.Workplane("XY").workplane(offset=z_top - depth)
            .pushPoints(points).circle(d / 2).extrude(depth))


def _io_window(z0, z1):
    return (cq.Workplane("XY").workplane(offset=z0)
            .center(OUT_X / 2, 0).rect(4 * WALL, 2 * IO_Y).extrude(z1 - z0))


def underside_points():
    pts = []
    for x, y in grid_points():
        if all((x - hx) ** 2 + (y - hy) ** 2 >= SKIP_NEAR_HOLE ** 2
               for hx, hy in BOARD_HOLES):
            pts.append((x, y))
    return pts


def deck_points():
    """Outer ring of the grid, minus the corners (those are lid screws)."""
    return [(x, y) for x, y in grid_points()
            if (abs(x) == 45.0) != (abs(y) == 55.0)]


def base():
    floor = (cq.Workplane("XY").rect(OUT_X, OUT_Y).extrude(FLOOR)
             .edges("|Z").fillet(CORNER_R))
    b = floor.union(_shell(FLOOR, SPLIT_Z)).union(_posts(FLOOR, SPLIT_Z))

    standoffs = (cq.Workplane("XY").workplane(offset=FLOOR)
                 .pushPoints(BOARD_HOLES).circle(STANDOFF_D / 2)
                 .extrude(STANDOFF_H))
    b = b.union(standoffs)

    # mounting grid: insert pockets from below
    b = b.cut(_holes(underside_points(), M3_INSERT_D, M3_INSERT_H, M3_INSERT_H))
    # board screws, self-tapping M2.5 x 8
    b = b.cut(_holes(BOARD_HOLES, M25_PILOT, PCB_Z, 8.0))
    # lid screw inserts in the corner posts
    b = b.cut(_holes(POSTS, M3_INSERT_D, SPLIT_Z, M3_INSERT_H))

    b = b.cut(_io_window(IO_Z0, SPLIT_Z + 1))

    # inlet slots in the back wall, below the heatsink
    slots = (cq.Workplane("YZ").workplane(offset=-OUT_X / 2 - 1)
             .pushPoints([(y, (FLOOR + 2 + SPLIT_Z - 3) / 2)
                          for y in range(-36, 37, 8)])
             .slot2D(SPLIT_Z - 3 - FLOOR - 2, 3.0, angle=90)
             .extrude(WALL + 2))
    b = b.cut(slots)

    # soften the underside edge so it sits flat without elephant foot
    return b.faces("<Z").edges().chamfer(0.6)


def lid():
    l = _shell(SPLIT_Z, ROOF_IN).union(_posts(SPLIT_Z, ROOF_IN))
    roof = (cq.Workplane("XY").workplane(offset=ROOF_IN)
            .rect(OUT_X, OUT_Y).extrude(ROOF_T)
            .edges("|Z").fillet(CORNER_R))
    l = l.union(roof)

    # deck bosses for the accessory grid
    boss_z0 = TOP_Z - M3_INSERT_H - 1.0
    bosses = (cq.Workplane("XY").workplane(offset=boss_z0)
              .pushPoints(deck_points()).circle(3.5).extrude(ROOF_IN - boss_z0))
    l = l.union(bosses)
    # keep the bosses inside the outer skin
    l = l.intersect(cq.Workplane("XY").workplane(offset=SPLIT_Z)
                    .rect(OUT_X, OUT_Y).extrude(TOP_Z - SPLIT_Z)
                    .edges("|Z").fillet(CORNER_R))

    l = l.cut(_holes(deck_points(), M3_INSERT_D, TOP_Z, M3_INSERT_H))

    # lid screws: clearance + head counterbore
    l = l.cut(_holes(POSTS, M3_CLEAR, TOP_Z + 1, TOP_Z + 1 - SPLIT_Z + 1))
    l = l.cut(_holes(POSTS, M3_HEAD, TOP_Z + 1, TOP_Z + 1 - LID_CBORE_Z))

    l = l.cut(_io_window(SPLIT_Z - 1, IO_Z1))

    # roof vents, three rows of slots between the deck bosses
    vents = []
    for x in range(-33, 34, 6):
        for y0, y1 in ((-46, -17), (-14, 14), (17, 46)):
            vents.append((x, (y0 + y1) / 2, y1 - y0))
    for x, yc, ln in vents:
        l = l.cut(cq.Workplane("XY").workplane(offset=ROOF_IN - 1)
                  .center(x, yc).slot2D(ln, 3.0, angle=90).extrude(ROOF_T + 2))

    # two RP-SMA antenna bulkheads in the back wall
    ant = (cq.Workplane("YZ").workplane(offset=-OUT_X / 2 - 1)
           .pushPoints([(y, ANT_Z) for y in ANT_Y]).circle(ANT_D / 2)
           .extrude(WALL + 2))
    l = l.cut(ant)

    # CSI ribbon slot in the -Y wall
    x0, x1, z0, z1 = CSI_SLOT
    l = l.cut(cq.Workplane("XY").workplane(offset=z0)
              .center((x0 + x1) / 2, -OUT_Y / 2).rect(x1 - x0, 4 * WALL)
              .extrude(z1 - z0))
    return l


def fit_test():
    """Thin frame with the four standoffs: check the hole pattern fast."""
    t = 2.0
    frame = (cq.Workplane("XY").rect(70, 98).extrude(t)
             .cut(cq.Workplane("XY").rect(48, 76).extrude(t)))
    frame = frame.translate((-5, -3, 0))
    st = (cq.Workplane("XY").pushPoints(BOARD_HOLES)
          .circle(STANDOFF_D / 2).extrude(t + STANDOFF_H))
    f = frame.union(st)
    return f.cut(_holes(BOARD_HOLES, M25_PILOT, t + STANDOFF_H + 1,
                        t + STANDOFF_H + 1))
