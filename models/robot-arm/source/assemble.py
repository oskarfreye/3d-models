"""Assembly + preview renders for the ST3215 robot arm.

Run with the repo venv:  .venv/bin/python models/robot-arm/source/assemble.py
"""
import os
import cadquery as cq
from cadquery import Assembly, Color

from params import *
from servo import servo_body, horn_adapter, tool_adapter, ADAPTER_TOP_Z
from links import link, turret, wrist
from base import base, base_lid, camera_mast
from gripper import body as gripper_body, jaw as gripper_jaw
from gripper import crank as gripper_crank, rod as gripper_rod
import gripper as grip

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "stl")
IMG = os.path.join(HERE, "..", "images")
os.makedirs(OUT, exist_ok=True)
os.makedirs(IMG, exist_ok=True)

ADAPTER_TOP = ADAPTER_TOP_Z          # 12.6


def servo_out_y(shape):
    """Servo local +Z output -> world +Y, case along -Z (pocket direction)."""
    return shape.rotate((0, 0, 0), (1, 0, 0), -90) \
                .rotate((0, 0, 0), (0, 1, 0), 90)


def assembly():
    a = Assembly()
    YEL = Color(0.95, 0.74, 0.1)
    ORA = Color(0.92, 0.45, 0.08)
    BLU = Color(0.16, 0.42, 0.78)
    GRY = Color(0.35, 0.35, 0.38)
    BLK = Color(0.12, 0.12, 0.14)
    STL = Color(0.72, 0.74, 0.78)
    WHT = Color(0.9, 0.9, 0.9)

    # ---- base -----------------------------------------------------------
    a.add(base().val(), name="base", color=YEL)
    a.add(base_lid().translate((0, 0, -0.01)).val(), name="lid", color=GRY)
    a.add(camera_mast().translate((0, -56, BASE_H + 19.8)).val(),
          name="mast", color=GRY)

    # ---- J1 -------------------------------------------------------------
    j1 = BASE_H
    a.add(servo_body().translate((0, 0, j1)).val(), name="servo1", color=BLK)
    a.add(horn_adapter().translate((0, 0, j1)).val(), name="ad1", color=STL)
    turret_z = j1 + ADAPTER_TOP
    a.add(turret().translate((0, 0, turret_z)).val(), name="turret", color=YEL)

    # ---- J2 -------------------------------------------------------------
    j2 = turret_z + 52.0
    a.add(servo_out_y(servo_body()).translate((0, 0, j2)).val(),
          name="servo2", color=BLK)
    a.add(servo_out_y(horn_adapter()).translate((0, 0, j2)).val(),
          name="ad2", color=STL)
    a.add(link(UPPER_ARM).translate((0, 0, j2)).val(), name="upper", color=ORA)

    # ---- J3 -------------------------------------------------------------
    j3 = j2 + UPPER_ARM
    a.add(servo_out_y(servo_body()).translate((0, 0, j3)).val(),
          name="servo3", color=BLK)
    a.add(servo_out_y(horn_adapter()).translate((0, 0, j3)).val(),
          name="ad3", color=STL)
    a.add(link(FOREARM).translate((0, 0, j3)).val(), name="fore", color=ORA)

    # ---- J4 / wrist -----------------------------------------------------
    j4 = j3 + FOREARM
    a.add(servo_out_y(servo_body()).translate((0, 0, j4)).val(),
          name="servo4", color=BLK)
    a.add(servo_out_y(horn_adapter()).translate((0, 0, j4)).val(),
          name="ad4", color=STL)
    a.add(wrist(WRIST_ROLL).translate((0, 0, j4)).val(),
          name="wrist", color=BLU)

    # ---- J5 -------------------------------------------------------------
    j5 = (0, 30, j4 + WRIST_ROLL)
    a.add(servo_body().translate(j5).val(), name="servo5", color=BLK)
    a.add(tool_adapter().translate(j5).val(), name="ad5", color=STL)
    tool_z = j5[2] + ADAPTER_TOP

    # ---- gripper (6th servo inside the tool) ----------------------------
    a.add(gripper_body().translate((0, 30, tool_z)).val(),
          name="grip", color=YEL)
    a.add(servo_body().rotate((0, 0, 0), (1, 1, 1), -120)
          .translate((0, 30, tool_z + grip.SERVO_Z)).val(),
          name="servo6", color=BLK)
    a.add(gripper_jaw().translate((-44, 30, tool_z)).val(),
          name="jaw", color=ORA)
    crankshape = (gripper_crank()
                  .rotate((0, 0, 0), (1, 1, 1), -120)
                  .translate((0, 0, grip.SERVO_Z))
                  .rotate((0, 0, grip.SERVO_Z), (0, 1, grip.SERVO_Z), 180)
                  .translate((0, 30, tool_z)))
    a.add(crankshape.val(), name="crank", color=STL)
    a.add(gripper_rod().translate((-29, 30, tool_z)).val(),
          name="rod", color=STL)

    info = {"j1": j1, "j2": j2, "j3": j3, "j4": j4,
            "j5": j5, "tool": tool_z}
    return a, info


if __name__ == "__main__":
    from render import render
    a, info = assembly()
    print("joints", {k: (round(v[2], 1) if isinstance(v, tuple) else round(v, 1))
                     for k, v in info.items()})
    try:
        a.save(os.path.join(OUT, "robot_arm_assembly.step"))
        print("wrote step")
    except Exception as e:
        print("step export failed:", e)
    render(a, os.path.join(IMG, "arm_straight.png"),
           direction=(0.65, 1.0, 0.25), width=900, height=1300,
           fov=28, pad=1.10)
    print("render done")
