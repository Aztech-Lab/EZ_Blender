# EZBlender asset presets

Paths are relative to the EZBlender package root (`main.py` directory).

| Preset | Use when | `scene_blend` | `init_script` | `render_script` |
|--------|----------|---------------|---------------|-----------------|
| `body` | body shape, muscular, thin, belly, shoulders | `blenderalch/starter_blends/body_shapekeys.blend` | `blenderalch/blender_scripts/shapekeys_examples/bodyshape.py` | `blenderalch/blender_base/bodyshape_shapekeys.py` |
| `face` | facial expression, smile, frown, wink, eyebrows | `blenderalch/starter_blends/face_animation.blend` | `blenderalch/blender_scripts/shapekeys_examples/facialshapekeys.py` | `blenderalch/blender_base/bodyshape_shapekeys.py` |
| `wineglass` | wine glass proportions / shapekeys | `blenderalch/starter_blends/wineglass_shapekeys.blend` | `blenderalch/blender_scripts/shapekeys_examples/wineglass.py` | `blenderalch/blender_base/bodyshape_shapekeys.py` |
| `lotion` | product bottle, studio lighting, gold/neon restyle | `blenderalch/starter_blends/lotion.blend` | `blenderalch/blender_scripts/lighting_examples/lotion.py` | `blenderalch/blender_base/lighting_adjustments.py` |
| `wood` | wood → marble / procedural materials | `blenderalch/starter_blends/BSDF_experiments.blend` | `blenderalch/blender_scripts/material_examples/infinigen_wood_example.py` | `blenderalch/blender_base/infinigen_render_materials.py` |
| `roses` | geometry-nodes roses | `blenderalch/starter_blends/roses.blend` | `blenderalch/blender_scripts/geonodes_example/roses.py` | `blenderalch/blender_base/geonodes.py` |

## Gallery outputs (reference demos)

| Folder | Preset | What it demonstrates |
|--------|--------|----------------------|
| `output/body1` | body | Chrome / metallic look on soft body |
| `output/body2` | body | Muscular bodybuilder shape keys |
| `output/body3` | body | Extreme muscular + belly shrink |
| `output/face1` | face | Tense / concerned expression |
| `output/lotion1` | lotion | Gold / chrome product material |
| `output/lotion2` | lotion | Warm mauve lighting |
| `output/lotion3` | lotion | Cyan–magenta cyberpunk |
| `output/lotion4` | lotion | Pink–cyan neon cyberpunk |

## Prompt tips

- **Shape only**: name shape attributes if known (`Abs`, `ChestEnlarge`, shoulders); otherwise say “more muscular / thinner belly”.
- **Material only**: “pure gold metallic, low roughness, mirror reflections”.
- **Lighting only**: “dark background, purple and cyan rim lights, low ambient HDR”.
- **Multi-domain**: one coherent style sentence works better than a long checklist (Planner will split tasks).
