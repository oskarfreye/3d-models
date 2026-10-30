# Camera Mount Knob

![Knob](images/vorschau_knauf.png)

Replacement clamping knob for the hinge on a phone/camera mount arm. It screws straight onto the M5 hinge bolt with no nut: the plain hole is slightly undersized, so the bolt cuts its own thread into the PETG. The knob presses on the 15.2 mm hinge disk to lock the angle.

## Parts

| File | Material / color | Notes |
|---|---|---|
| `stl/knauf.stl` | PETG | The knob, already flipped for printing (flat top on the bed) |
| `stl/passtest_loecher.stl` | PETG | Optional: plate with 4.1 / 4.3 / 4.5 mm holes (1/2/3 notches) to find the hole size that bites best |

## Print settings

- Printer: Bambu Lab A1 mini
- Layer height: 0.16–0.2 mm
- Walls: 4+, infill 50 %+ (the thread is cut into the walls around the hole)
- Supports: none

## Fitting

1. Back the bolt out if needed so its tip is accessible, start the knob straight, and turn it on. It will be stiff the first time because it's cutting the thread.
2. Tighten by hand to lock the hinge.

The bolt only sticks out about 2.3 mm past the disk (44.65 − 42.34 mm), so the knob gets about 3 thread turns. That holds a phone, but if it strips or slips, fit a bolt about 5 mm longer. The hole is 8 mm deep and takes it without changes.

## Customizing

All dimensions are at the top of `source/knauf.scad`:

- `loch_d`: hole size (use the fit test result)
- `griff_d`: grip diameter, 20 mm by default for more torque; set it to `14.25` for a knob flush with the hinge disk
- `auflage_d`: diameter of the clamping face (14.25 mm)

```sh
openscad -o stl/knauf.stl -D 'part="knauf"' -D 'loch_d=4.1' source/knauf.scad
```
