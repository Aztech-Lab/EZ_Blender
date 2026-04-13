# -*- coding: utf-8 -*-
"""
Created on Tue Aug 19 21:50:01 2025

@author: MaxGr
"""

# blender_base/passthrough.py
import os
import sys
import runpy

argv = sys.argv
if "--" in argv:
    argv = argv[argv.index("--") + 1:]
else:
    argv = []

if len(argv) < 2:
    raise RuntimeError("Usage: blender --python passthrough.py -- <script_path> <render_path>")

script_path = os.path.abspath(argv[0])
render_path = os.path.abspath(argv[1])
os.makedirs(os.path.dirname(render_path), exist_ok=True)

# Provide the render path to the child script
os.environ["BLENDER_ALCHEMY_RENDER_PATH"] = render_path
globals()["BLENDER_ALCHEMY_RENDER_PATH"] = render_path

print(f"[passthrough] script={script_path}")
print(f"[passthrough] render={render_path}")

runpy.run_path(script_path, run_name="__main__")
