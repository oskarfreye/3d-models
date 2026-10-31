"""Shared dimensions for the modular Jetson Nano case.

All values in millimetres.

Case frame
----------
Origin is the centre of the case footprint, Z = 0 is the underside of
the floor. +X is the I/O side (barrel jack, HDMI, DP, USB, RJ45,
micro-USB). -Y is the barrel-jack / CSI end, +Y the micro-USB /
40-pin-header end.

Board data
----------
Jetson Nano Developer Kit, carrier P3449 rev A02 (also fits B01, same
outline and hole pattern). NVIDIA does not publish connector
coordinates, so the hole pattern and I/O window were measured from the
STEP files of github.com/dudasdavid/Jetson-nano-case. The window is
deliberately generous; print `fit_test` first to check the holes.
"""

# --- printer ---------------------------------------------------------------
BED = 180.0

# --- fasteners -------------------------------------------------------------
M3_CLEAR = 3.4
M3_HEAD = 6.4           # counterbore for M3 socket heads
M3_INSERT_D = 4.0       # ruthex M3 x 5.7 datasheet hole
M3_INSERT_H = 6.5
M25_PILOT = 2.2         # M2.5 self-tapping into PETG
M2_PILOT = 1.8          # M2 self-tapping into PETG

# --- mounting grid ---------------------------------------------------------
# Every mounting point (floor underside, top deck, accessories) sits on
# this 10 mm grid. Points are at odd multiples of 5 so the grid is
# centred on the case: X = -45 .. 45, Y = -55 .. 55.
GRID = 10.0
GRID_NX = 10
GRID_NY = 12


def grid_points():
    return [(-45.0 + GRID * i, -55.0 + GRID * j)
            for i in range(GRID_NX) for j in range(GRID_NY)]


# --- board -----------------------------------------------------------------
BOARD_X = 80.0
BOARD_Y = 100.0
PCB_T = 1.6
# Mounting holes, 58 x 86 pattern; the I/O edge holes are 16 mm in from
# the edge (the module overhangs there), the back ones 6 mm.
BOARD_HOLES = [(-34.0, -46.0), (24.0, -46.0), (-34.0, 40.0), (24.0, 40.0)]

# --- case ------------------------------------------------------------------
OUT_X = 100.0
OUT_Y = 120.0
WALL = 3.0
CORNER_R = 5.0                  # outer corner radius
FLOOR = 7.0                     # holds the underside insert pockets
STANDOFF_H = 6.0
STANDOFF_D = 6.5

PCB_Z = FLOOR + STANDOFF_H      # 13.0, PCB underside
PCB_TOP = PCB_Z + PCB_T         # 14.6

SPLIT_Z = 22.0                  # base / lid joint
ROOF_IN = PCB_TOP + 30.4        # 45.0, heatsink is ~27 above the PCB
ROOF_T = 3.0
TOP_Z = ROOF_IN + ROOF_T        # 48.0

# Lid screws: M3 x 16 from the top through the lid corner posts into
# inserts in the base posts. The posts are the four corner grid points.
POST_R = 5.0
POSTS = [(sx * 45.0, sy * 55.0) for sx in (-1, 1) for sy in (-1, 1)]
LID_CBORE_Z = 34.0              # bottom of the head counterbore

# I/O window on the +X side, from just below the PCB to above the
# stacked USB ports (16 mm) plus clearance.
IO_Z0 = PCB_Z - 0.5
IO_Z1 = PCB_TOP + 17.5
IO_Y = 50.0                     # +-, ends at the corner posts

# Peripherals
ANT_D = 6.5                     # RP-SMA bulkhead
ANT_Y = (-20.0, 20.0)           # on the -X wall
ANT_Z = 34.5
CSI_SLOT = (-20.0, 12.0, 37.0, 40.0)   # x0, x1, z0, z1 in the -Y wall

# --- Raspberry Pi Camera v2 ------------------------------------------------
CAM_W = 25.0
CAM_H = 23.86
CAM_HOLES_X = 21.0
CAM_HOLE_Z = (9.36, 21.86)      # from the connector (bottom) edge
