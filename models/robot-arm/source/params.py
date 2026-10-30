"""Shared dimensions for the ST3215 desktop robot arm.

All values in millimetres. The servo datasheet (Waveshare ST3215)
and the official STEP model were used as the source of truth.

Servo local frame
-----------------
Z is the output axis, +Z points out of the horn.
The case front face (the plane the bracket sits on) is Z = 0.
X runs along the 45.22 mm length, Y along the 24.72 mm width.
The output axis is at X = 0, Y = 0, so the case spans
X = -10.11 .. +35.11 and Y = -12.36 .. +12.36.
"""

# --- printer ---------------------------------------------------------------
BED = 180.0
NOZZLE = 0.4

# --- ST3215 servo ----------------------------------------------------------
SERVO_L = 45.22
SERVO_W = 24.72
SERVO_BODY_H = 29.0
SERVO_CAP_OUT = 2.1       # metal output cap above the case front
SERVO_CAP_REAR = 3.35     # rear bearing cap below the case
SERVO_BACK = -(SERVO_BODY_H + SERVO_CAP_REAR)   # -32.35

AXIS_FROM_END = 10.11     # output axis from the "short" end of the case
HORN_D = 19.2
HORN_BCD = 14.0           # 4 x M2 on this bolt circle
HORN_TOP = SERVO_CAP_OUT

# 4 x M2 mounting holes on the output face (self-tapping, 1.6 mm pilot)
MOUNT_X = (AXIS_FROM_END + 8.3, AXIS_FROM_END + 8.3 + 20.7)  # 8.30 / 29.00
MOUNT_Y = 10.25

# --- joint stack -----------------------------------------------------------
PLATE_T = 5.0             # parent face plate thickness
PLATE_HOLE = 20.0         # clearance around the 19.2 mm horn
ADAPTER_SPIGOT = 18.8
ADAPTER_SPIGOT_H = PLATE_T - HORN_TOP          # 2.9
ADAPTER_FLANGE_D = 36.0
ADAPTER_FLANGE_T = 7.0
ADAPTER_TOP = PLATE_T + ADAPTER_FLANGE_T       # 12.0
CHILD_FLANGE_T = 6.0
CHILD_FLANGE_W = 36.0

# 4 x M3 heat-set inserts on a 26 mm bolt circle (at 0/90/180/270)
M3_BCD = 26.0
M3_INSERT_D = 4.6
M3_INSERT_H = 6.0

# screws used
M2_CLEAR = 2.3
M3_CLEAR = 3.4
M3_HEAD = 6.2

# --- arm -------------------------------------------------------------------
J1_HEIGHT = 52.0          # base top plate -> J1 output face
TURRET_RISE = 58.0        # J1 output -> J2 axis
UPPER_ARM = 118.0         # J2 -> J3
FOREARM = 108.0           # J3 -> J4
WRIST_ROLL = 58.0         # J4 -> J5
TOOL_FLANGE = 12.6        # J5 output -> tool face (adapter top)

REACH = UPPER_ARM + FOREARM + WRIST_ROLL + TOOL_FLANGE

# --- base ------------------------------------------------------------------
BASE_W = 150.0
BASE_D = 150.0
BASE_H = 46.0
