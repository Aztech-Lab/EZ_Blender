"""
Given a python file (indicated inthe commandline path), render the material output.
"""

import bpy
import random
import json
import os
import sys
from sys import platform



if __name__ == "__main__":

    # code_fpath = sys.argv[6]  # TODO: allow a folder to be given, each with a possible guess.
    # rendering_fpath = sys.argv[7] # rendering

    # ========================================================
    # robust argv parsing: read args after '--'
    if '--' in sys.argv:
        i = sys.argv.index('--') + 1
        code_fpath = sys.argv[i]
        rendering_fpath = sys.argv[i + 1]
    else:
        # fallback to old indexing if needed
        code_fpath = sys.argv[6]
        rendering_fpath = sys.argv[7]
    # ========================================================


    bpy.context.scene.render.engine = "CYCLES"
    # setting up Rendering settings
    if platform == "linux" or platform == "linux2":
        # linux
        bpy.context.preferences.addons[
            "cycles"
        ].preferences.compute_device_type = "CUDA"
        bpy.context.scene.cycles.device = "GPU"   
        
    elif platform == "darwin":
        # OS X
        bpy.context.preferences.addons[
            "cycles"
        ].preferences.compute_device_type = "METAL"
        
    # elif platform == "win32":
    #     # Windows...
    #     raise NotImplemented("Not supported")
    
    # ========================================================
    elif platform == "win32":
        # Windows: try GPU backends, fallback to CPU
        prefs = bpy.context.preferences.addons["cycles"].preferences
        ok = False
        for backend in ("OPTIX", "CUDA", "HIP", "ONEAPI"):  # NVIDIA / AMD / Intel
            try:
                prefs.compute_device_type = backend
                # enable all devices of this backend
                for dev in prefs.devices:
                    try:
                        dev.use = True
                    except Exception:
                        pass
                bpy.context.scene.cycles.device = "GPU"
                print(f"[Cycles] Using GPU backend: {backend}")
                ok = True
                break
            except Exception:
                pass
        if not ok:
            bpy.context.scene.cycles.device = "CPU"
            print("[Cycles] GPU not available; using CPU.")
    # ========================================================


    # bpy.context.preferences.addons["cycles"].preferences.get_devices()
    # print(bpy.context.preferences.addons["cycles"].preferences.compute_device_type)
    # for d in bpy.context.preferences.addons["cycles"].preferences.devices:
    #     d["use"] = 1 # Using all devices, include GPU and CPU
    #     print(d["name"], d["use"])

    # ========================================================
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.get_devices()
    print(prefs.compute_device_type)
    for dev in prefs.devices:
        try:
            dev.use = True
        except Exception:
            pass
        print(getattr(dev, "name", "device"), getattr(dev, "use", None))
    # ========================================================
    

    bpy.context.scene.render.resolution_x = 512
    bpy.context.scene.render.resolution_y = 512

    
    # creating the material and assigning it to the sphere
    with open(code_fpath, "r") as f:
        code = f.read()
    try:
        exec(code)
    except:
        raise ValueError
    
    # ========================================================
    # ensure a camera exists
    if bpy.context.scene.camera is None:
        bpy.ops.object.camera_add(location=(6, -6, 5))
        bpy.context.scene.camera = bpy.context.active_object
    
    # make sure the output directory exists
    os.makedirs(os.path.dirname(rendering_fpath), exist_ok=True)
    # ========================================================

    # ========================================================
    scene = bpy.context.scene
    scene.cycles.volume_bounces = 2
    
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.use_denoising = True
    scene.cycles.sample_clamp_indirect = 2.0
    scene.cycles.caustics_reflective = False
    scene.cycles.caustics_refractive = False
    
    scene.cycles.samples = 96
    scene.cycles.preview_samples = 24
    scene.cycles.max_bounces = 4
    scene.cycles.diffuse_bounces = 1
    scene.cycles.glossy_bounces = 2
    scene.cycles.transmission_bounces = 2
    # ========================================================

    
    # render, and save.
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = rendering_fpath
    bpy.ops.render.render(write_still=True)
    print(f"[Render] Saved: {rendering_fpath}")


    # print( f"Poppping material at index {material_index}")
    # save to disk
    # material_obj.data.materials.pop(index=material_index)

    
