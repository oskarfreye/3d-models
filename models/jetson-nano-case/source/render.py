"""Small offscreen VTK renderer with explicit three-point lighting.

CadQuery's vis.show uses the default renderer light, which leaves +Z faces
dark. This helper adds proper scene lights and fits the camera to the model
without the elevation/azimuth quirks.
"""
import math
import cadquery as cq
from cadquery.occ_impl.assembly import toVTKAssy
from cadquery.vis import _to_assy

from vtkmodules.vtkRenderingCore import (
    vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor,
    vtkWindowToImageFilter, vtkLight,
)
from vtkmodules.vtkIOImage import vtkPNGWriter


def _bounds(obj):
    if isinstance(obj, cq.Assembly):
        shapes = [o.obj for o in obj.objects.values() if o.obj is not None]
    else:
        shapes = [obj.val() if hasattr(obj, "val") else obj]
    bbs = [s.BoundingBox() for s in shapes]
    lo = [min(b.xmin for b in bbs), min(b.ymin for b in bbs),
          min(b.zmin for b in bbs)]
    hi = [max(b.xmax for b in bbs), max(b.ymax for b in bbs),
          max(b.zmax for b in bbs)]
    center = tuple((a + b) / 2 for a, b in zip(lo, hi))
    size = max(b - a for a, b in zip(lo, hi))
    return center, size


def render(obj, path, direction=(0.6, -1.0, 0.35), width=900, height=1200,
           fov=30.0, bg=(0.97, 0.97, 0.97), pad=1.12, zoom=1.0):
    renderer = vtkRenderer()
    assy = obj if isinstance(obj, cq.Assembly) else _to_assy(obj)
    for act in toVTKAssy(assy):
        renderer.AddActor(act)

    focus, size = _bounds(obj)

    dist = pad * (size / 2.0) / math.tan(math.radians(fov) / 2.0)

    d = cq.Vector(*direction).normalized()
    pos = (focus[0] + d.x * dist, focus[1] + d.y * dist,
           focus[2] + d.z * dist)

    renderer.RemoveAllLights()
    key = vtkLight()
    key.SetPosition(pos[0] + 400, pos[1] - 600, pos[2] + 900)
    key.SetFocalPoint(*focus)
    key.SetIntensity(0.9)
    fill = vtkLight()
    fill.SetPosition(pos[0] - 900, pos[1] + 400, pos[2] + 300)
    fill.SetFocalPoint(*focus)
    fill.SetIntensity(0.5)
    rim = vtkLight()
    rim.SetPosition(focus[0], focus[1] + 1200, focus[2] + 600)
    rim.SetFocalPoint(*focus)
    rim.SetIntensity(0.45)
    for l in (key, fill, rim):
        renderer.AddLight(l)
    renderer.SetBackground(*bg)
    renderer.GradientBackgroundOn()

    cam = renderer.GetActiveCamera()
    cam.SetPosition(*pos)
    cam.SetFocalPoint(*focus)
    cam.SetViewUp(0, 0, 1)
    cam.SetViewAngle(fov)
    renderer.ResetCameraClippingRange()

    win = vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.AddRenderer(renderer)
    win.SetSize(width, height)
    inter = vtkRenderWindowInteractor()
    inter.SetRenderWindow(win)
    inter.Initialize()
    cam.Zoom(zoom)
    win.Render()

    f = vtkWindowToImageFilter()
    f.SetInput(win)
    f.SetInputBufferTypeToRGB()
    f.ReadFrontBufferOff()
    f.Update()
    w = vtkPNGWriter()
    w.SetFileName(path)
    w.SetInputConnection(f.GetOutputPort())
    w.Write()
    return path
