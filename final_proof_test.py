import os
from ezblender import run_blender

blender_exe = "E:/2025/Blender/blender/blender.exe"
scene_blend = "starter_blends/lotion.blend"
init_script = "blender_scripts/simple_neon.py"
render_script = "blender_base/lighting_adjustments.py"
result_img = "./output/final_proof.png"

print(f"Rendering to: {result_img}")
result = run_blender(blender_exe, scene_blend, init_script, render_script, result_img)

if result['status']:
    print(f"✅ SUCCESS! Image created at {result_img}")
else:
    print("❌ Still failed.")
    print("STDOUT:", result.get('stdout', '')[-500:])
    print("STDERR:", result.get('stderr', '')[-500:])
