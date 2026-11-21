"""
Public-version branding and massing (pipeline/design_variation.py).

The model is built from a real submission drawing. For the public version the building gets its own
name and a deliberately different silhouette: floors 2-7 and the terrace twist a little more each
storey and step in slightly, so the tower is no longer a copy of the drawn massing. Ground, basement
and floor 1 (the interiors and most 360° spots) are untouched.

Everything is driven by the two constants below; change them and run `python build.py build`.
"""

from __future__ import annotations

import math
import re

import bpy
from mathutils import Matrix, Vector

BUILDING_NAME = "NAUGHTY DEVELOPER"

# Plan centre of the typical floor slab (x 0..13.12, y 0..38.73) in building metres
PIVOT = (6.56, 19.37)
FIRST_FLOOR = 2           # floors below this keep the drawn plan
TWIST_DEG_PER_FLOOR = 1.0
TAPER_PER_FLOOR = 0.008   # plan scale lost per floor above FIRST_FLOOR - 1
TERRACE_INDEX = 8


def floor_transform(floor_index: int) -> tuple[float, float]:
    """(rotation in radians, plan scale) applied to a floor; the drawn plan below FIRST_FLOOR."""
    steps = max(0, floor_index - (FIRST_FLOOR - 1))
    return math.radians(TWIST_DEG_PER_FLOOR * steps), 1.0 - TAPER_PER_FLOOR * steps


def _matrix(floor_index: int) -> Matrix:
    angle, scale = floor_transform(floor_index)
    px, py = PIVOT
    return (Matrix.Translation((px, py, 0.0)) @ Matrix.Rotation(angle, 4, "Z")
            @ Matrix.Diagonal((scale, scale, 1.0, 1.0)) @ Matrix.Translation((-px, -py, 0.0)))


def shift_point(x: float, y: float, floor_index: int) -> tuple[float, float, float]:
    """Where a plan point ends up on a twisted floor, plus the rotation (degrees) a camera there must add."""
    m = _matrix(floor_index)
    p = m @ Vector((x, y, 0.0))
    return p.x, p.y, math.degrees(floor_transform(floor_index)[0])


def _floor_index(collection_name: str) -> int | None:
    m = re.fullmatch(r"Floor_(\d+)(?:_Terrace)?", collection_name)
    return int(m.group(1)) if m else None


def apply_shape_variation() -> dict[int, tuple[float, float]]:
    """Twist and taper every floor collection from FIRST_FLOOR up (terrace included)."""
    applied = {}
    for coll in bpy.data.collections:
        idx = _floor_index(coll.name)
        if idx is None or idx < FIRST_FLOOR:
            continue
        m = _matrix(idx)
        for obj in coll.objects:
            if obj.type == "MESH":
                obj.data.transform(m)
                obj.data.update()
            else:
                obj.location = m @ obj.location
                obj.rotation_euler.z += floor_transform(idx)[0]
        applied[idx] = floor_transform(idx)
    return applied


def add_name_sign(name: str, collection, material, location, rotation, size: float, extrude: float = 0.10,
                  text: str = BUILDING_NAME):
    """Extruded 3D lettering in the scene (converted to mesh by export.py for the .glb)."""
    curve = bpy.data.curves.new(type="FONT", name=f"{name}_Font")
    curve.body = text
    curve.size = size
    curve.extrude = extrude
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation
    obj.data.materials.append(material)
    return obj
