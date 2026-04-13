# -*- coding: utf-8 -*-
"""
Created on Tue Aug 19 21:50:20 2025

@author: MaxGr
"""

# blender_scripts/_debug_render.py
import os
import bpy
import math

render_path = os.environ.get("BLENDER_ALCHEMY_RENDER_PATH") or globals().get("BLENDER_ALCHEMY_RENDER_PATH")
if not render_path:
    raise RuntimeError("No render path provided (env/global BLENDER_ALCHEMY_RENDER_PATH).")

# Set render settings
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.filepath = render_path

# Add a camera
bpy.ops.object.camera_add(location=(3, -3, 2), rotation=(math.radians(60), 0, math.radians(45)))
scene.camera = bpy.context.active_object

# Add a sun light
bpy.ops.object.light_add(type='SUN', location=(4, -2, 6))

# Ensure output folder exists
os.makedirs(os.path.dirname(render_path), exist_ok=True)

# Render to file
print(f"[debug_render] writing to: {render_path}")
bpy.ops.render.render(write_still=True)
