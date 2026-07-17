# placidusax_arena.py
# Create an Elden Ring "Dragonlord arena"-style scene using only Blender Python (procedural)
# Tested on Blender 4.x API style (should also work on 3.x with minor/no changes)

import bpy
import bmesh
import random
import math
from math import radians
from mathutils import Vector, Euler

# -----------------------------
# Helpers
# -----------------------------
# ---------- GLOBAL TOGGLES (safe defaults) ----------
ENABLE_FOG = True            # background fog volumes
ENABLE_COMPOSITOR = True     # bloom/vignette
SAFE_RENDER_EXPOSURE = 1.2   # small lift to avoid underexposure

def clean_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)
    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)

def set_render_settings():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 6
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.use_preview_adaptive_sampling = True
    scene.cycles.preview_samples = 16
    scene.cycles.filter_width = 1.2
    scene.view_settings.look = 'Medium High Contrast'
    scene.world = bpy.data.worlds.new("World")
    scene.world.use_nodes = True

    # Stormy world shader
    nt = scene.world.node_tree
    nodes = nt.nodes
    links = nt.links
    for n in nodes: nodes.remove(n)

    w_out = nodes.new("ShaderNodeOutputWorld")
    w_bg = nodes.new("ShaderNodeBackground")
    w_mix = nodes.new("ShaderNodeMixRGB")
    w_noise = nodes.new("ShaderNodeTexNoise")
    w_coord = nodes.new("ShaderNodeTexCoord")
    w_ramp = nodes.new("ShaderNodeValToRGB")

    w_bg.inputs[1].default_value = 1.0
    w_bg.inputs[0].default_value = (0.02, 0.02, 0.025, 1.0)  # dark base

    w_noise.inputs["Scale"].default_value = 3.5
    w_noise.inputs["Detail"].default_value = 8.0
    w_noise.inputs["Roughness"].default_value = 0.55

    w_ramp.color_ramp.elements[0].position = 0.35
    w_ramp.color_ramp.elements[0].color = (0.02, 0.02, 0.03, 1)
    w_ramp.color_ramp.elements[1].position = 0.85
    w_ramp.color_ramp.elements[1].color = (0.08, 0.08, 0.1, 1)

    w_mix.blend_type = 'ADD'
    w_mix.inputs['Fac'].default_value = 1.0

    links.new(w_coord.outputs['Generated'], w_noise.inputs['Vector'])
    links.new(w_noise.outputs['Fac'], w_ramp.inputs['Fac'])
    links.new(w_ramp.outputs['Color'], w_mix.inputs['Color2'])
    links.new(w_bg.outputs['Background'], w_mix.inputs['Color1'])
    links.new(w_mix.outputs['Color'], w_out.inputs['Surface'])

def look_at(obj, target=Vector((0,0,0))):
    direction = (target - obj.location).to_track_quat('Z', 'Y')
    obj.rotation_euler = direction.to_euler()

def add_camera_and_keylight():
    # Camera
    bpy.ops.object.camera_add(location=(0.0, -36.0, 10.0))
    cam = bpy.context.object
    look_at(cam, Vector((0, 0, 0)))
    cam.data.lens = 10
    cam.data.clip_end = 1000

    # Sun light
    bpy.ops.object.light_add(type='SUN', location=(20, -20, 50))
    sun = bpy.context.object
    sun.data.energy = 2.5
    sun.data.angle = radians(10)
    sun.rotation_euler = Euler((radians(50), radians(-20), radians(-30)), 'XYZ')

    # Fill area
    bpy.ops.object.light_add(type='AREA', location=(-10, -10, 12))
    area = bpy.context.object
    area.data.energy = 2000
    area.data.size = 15.0

    return cam

# -----------------------------
# Materials (procedural)
# -----------------------------
def make_platform_material():
    mat = bpy.data.materials.new("Mat_Platform")
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    for n in nodes: nodes.remove(n)

    out = nodes.new("ShaderNodeOutputMaterial")
    princ = nodes.new("ShaderNodeBsdfPrincipled")
    princ.inputs['Specular'].default_value = 0.12
    princ.inputs['Roughness'].default_value = 0.95
    princ.inputs['Base Color'].default_value = (0.12, 0.12, 0.12, 1)

    # Crack mask: Voronoi distance + ramp
    vor = nodes.new("ShaderNodeTexVoronoi")
    vor.feature = 'DISTANCE_TO_EDGE'
    vor.distance = 'EUCLIDEAN'
    vor.inputs['Scale'].default_value = 12.0

    ramp_crack = nodes.new("ShaderNodeValToRGB")
    ramp_crack.color_ramp.elements[0].position = 0.02
    ramp_crack.color_ramp.elements[0].color = (0,0,0,1)
    ramp_crack.color_ramp.elements[1].position = 0.1
    ramp_crack.color_ramp.elements[1].color = (1,1,1,1)

    # Musgrave/Bump for relief
    mus = nodes.new("ShaderNodeTexMusgrave")
    mus.inputs['Scale'].default_value = 3.0
    mus.inputs['Detail'].default_value = 8.0
    mus.inputs['Dimension'].default_value = 0.7

    bump = nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = 0.6
    bump.inputs['Distance'].default_value = 0.2

    # Mix gold into cracks
    mix_col = nodes.new("ShaderNodeMixRGB")
    mix_col.blend_type = 'MIX'
    mix_col.inputs['Fac'].default_value = 0.8

    gold = nodes.new("ShaderNodeRGB")
    gold.outputs['Color'].default_value = (0.8, 0.65, 0.2, 1.0)

    tex_coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs['Scale'].default_value = (0.4, 0.4, 0.4)

    # Links
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], vor.inputs['Vector'])
    links.new(mapping.outputs['Vector'], mus.inputs['Vector'])

    links.new(vor.outputs['Distance'], ramp_crack.inputs['Fac'])
    links.new(mus.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], princ.inputs['Normal'])

    links.new(ramp_crack.outputs['Color'], mix_col.inputs['Fac'])
    links.new(gold.outputs['Color'], mix_col.inputs['Color2'])
    links.new(princ.inputs['Base Color'], mix_col.inputs['Color1'])

    links.new(mix_col.outputs['Color'], princ.inputs['Base Color'])
    links.new(princ.outputs['BSDF'], out.inputs['Surface'])

    # Use bump only displacement
    mat.cycles.displacement_method = 'BUMP'
    return mat

def make_stone_ruin_material():
    mat = bpy.data.materials.new("Mat_RuinStone")
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    for n in nodes: nodes.remove(n)

    out = nodes.new("ShaderNodeOutputMaterial")
    princ = nodes.new("ShaderNodeBsdfPrincipled")
    princ.inputs['Base Color'].default_value = (0.1,0.1,0.1,1)
    princ.inputs['Roughness'].default_value = 0.95
    princ.inputs['Specular'].default_value = 0.05

    mus = nodes.new("ShaderNodeTexMusgrave")
    mus.inputs['Scale'].default_value = 6.0
    mus.inputs['Detail'].default_value = 12.0

    bump = nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = 0.8
    bump.inputs['Distance'].default_value = 0.15

    links.new(mus.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], princ.inputs['Normal'])
    links.new(princ.outputs['BSDF'], out.inputs['Surface'])
    mat.cycles.displacement_method = 'BUMP'
    return mat

def make_emission_material(name, color=(1,0.2,0.05,1), strength=15.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    for n in nodes: nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    em = nodes.new("ShaderNodeEmission")
    em.inputs['Color'].default_value = color
    em.inputs['Strength'].default_value = strength
    links.new(em.outputs['Emission'], out.inputs['Surface'])
    return mat

def make_volume_fog_material():
    mat = bpy.data.materials.new("Mat_VolFog")
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    for n in nodes: nodes.remove(n)

    out = nodes.new("ShaderNodeOutputMaterial")
    vol = nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs['Anisotropy'].default_value = 0.3
    vol.inputs['Color'].default_value = (0.9, 0.85, 0.95, 1)

    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs['Scale'].default_value = 1.5
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.65

    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[1].position = 0.8

    coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs['Scale'].default_value = (0.5, 0.5, 0.35)

    links.new(coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], vol.inputs['Density'])
    links.new(vol.outputs['Volume'], out.inputs['Volume'])
    return mat

def make_wall_material():
    mat = bpy.data.materials.new("Mat_WallRelief")
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    for n in nodes: nodes.remove(n)

    out = nodes.new("ShaderNodeOutputMaterial")
    princ = nodes.new("ShaderNodeBsdfPrincipled")
    princ.inputs['Base Color'].default_value = (0.12, 0.12, 0.13, 1)
    princ.inputs['Roughness'].default_value = 0.95
    princ.inputs['Specular'].default_value = 0.06

    # Cylindrical UV-ish mapping via Object coords
    tex_coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")

    # Periodic bands around the wall (angular)
    wave_ang = nodes.new("ShaderNodeTexWave")
    wave_ang.wave_type = 'RINGS'          # concentric, we'll fake angular by mapping
    wave_ang.inputs['Scale'].default_value = 6.0
    wave_ang.inputs['Distortion'].default_value = 0.0
    wave_ang.inputs['Detail'].default_value = 2.0

    # Vertical bands
    wave_vert = nodes.new("ShaderNodeTexWave")
    wave_vert.wave_type = 'BANDS'
    wave_vert.inputs['Scale'].default_value = 24.0
    wave_vert.inputs['Distortion'].default_value = 0.0
    wave_vert.inputs['Detail'].default_value = 2.0

    # Carving noise
    vor = nodes.new("ShaderNodeTexVoronoi")
    vor.feature = 'F1'
    vor.inputs['Scale'].default_value = 40.0

    mus = nodes.new("ShaderNodeTexMusgrave")
    mus.inputs['Scale'].default_value = 8.0
    mus.inputs['Detail'].default_value = 12.0
    mus.inputs['Dimension'].default_value = 0.7

    # Combine patterns into relief mask
    mix1 = nodes.new("ShaderNodeMixRGB"); mix1.blend_type = 'MULTIPLY'; mix1.inputs['Fac'].default_value = 0.6
    mix2 = nodes.new("ShaderNodeMixRGB"); mix2.blend_type = 'ADD';       mix2.inputs['Fac'].default_value = 0.5
    ramp_relief = nodes.new("ShaderNodeValToRGB")
    ramp_relief.color_ramp.elements[0].position = 0.25
    ramp_relief.color_ramp.elements[1].position = 0.55

    # Bump
    bump = nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = 0.5
    bump.inputs['Distance'].default_value = 0.6

    # Slight color variation into cracks/grooves
    mix_col = nodes.new("ShaderNodeMixRGB"); mix_col.blend_type = 'MIX'
    mix_col.inputs['Fac'].default_value = 0.25
    dark_accent = nodes.new("ShaderNodeRGB"); dark_accent.outputs['Color'].default_value = (0.08, 0.08, 0.09, 1)

    # Links (map object space -> textures)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], wave_ang.inputs['Vector'])
    links.new(mapping.outputs['Vector'], wave_vert.inputs['Vector'])
    links.new(mapping.outputs['Vector'], vor.inputs['Vector'])
    links.new(mapping.outputs['Vector'], mus.inputs['Vector'])

    # Combine patterns
    links.new(wave_ang.outputs['Color'], mix1.inputs['Color1'])
    links.new(wave_vert.outputs['Color'], mix1.inputs['Color2'])
    links.new(mix1.outputs['Color'], mix2.inputs['Color1'])
    links.new(vor.outputs['Distance'], mix2.inputs['Color2'])

    links.new(mix2.outputs['Color'], ramp_relief.inputs['Fac'])
    links.new(ramp_relief.outputs['Color'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], princ.inputs['Normal'])

    links.new(princ.outputs['BSDF'], out.inputs['Surface'])

    # Subtle color modulation
    links.new(princ.inputs['Base Color'], mix_col.inputs['Color1'])
    links.new(mus.outputs['Fac'], mix_col.inputs['Fac'])
    links.new(dark_accent.outputs['Color'], mix_col.inputs['Color2'])
    links.new(mix_col.outputs['Color'], princ.inputs['Base Color'])

    mat.cycles.displacement_method = 'BUMP'
    return mat


def create_outer_wall(inner_radius=22.0, thickness=2.5, height=10.0,
                      pilaster_count=48, merlon_count=64):
    """
    Build a ring wall with inner radius, uniform thickness, periodic pilasters and merlons.
    """
    mat = make_wall_material()
    # Main ring (difference of two cylinders)
    # Outer
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=inner_radius+thickness, depth=height, location=(0,0,height/2))
    outer = bpy.context.object; outer.name = "Wall_Outer"
    # Inner
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=inner_radius, depth=height*1.2, location=(0,0,height/2))
    inner = bpy.context.object; inner.name = "Wall_Inner"

    # Boolean difference
    bpy.ops.object.select_all(action='DESELECT')
    outer.select_set(True); bpy.context.view_layer.objects.active = outer
    bpy.ops.object.modifier_add(type='BOOLEAN')
    outer.modifiers[-1].operation = 'DIFFERENCE'
    outer.modifiers[-1].object = inner
    bpy.ops.object.modifier_apply(modifier=outer.modifiers[-1].name)
    bpy.data.objects.remove(inner, do_unlink=True)

    # Bevel for nice catches
    bpy.ops.object.modifier_add(type='BEVEL')
    outer.modifiers['Bevel'].width = 0.05
    outer.modifiers['Bevel'].segments = 2
    outer.data.materials.append(mat)

    # Pilasters (vertical buttresses)
    pilasters = []
    for i in range(pilaster_count):
        ang = 2*math.pi * i / pilaster_count
        r_mid = inner_radius - thickness*0.1
        x = r_mid*math.cos(ang)
        y = r_mid*math.sin(ang)
        w = thickness*0.6
        d = 0.6
        h = height*1.05

        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, h/2))
        p = bpy.context.object
        p.name = f"Pilaster_{i}"
        p.scale = (w/2, d/2, h/2)
        p.rotation_euler[2] = ang
        # tiny bevel
        bpy.ops.object.modifier_add(type='BEVEL')
        p.modifiers['Bevel'].width = 0.03
        p.modifiers['Bevel'].segments = 2
        p.data.materials.append(mat)
        pilasters.append(p)

    # Merlons / crenellations (teeth on top)
    merlons = []
    top_z = height
    for i in range(merlon_count):
        ang = 2*math.pi * i / merlon_count
        r = inner_radius + thickness*0.5
        x = r*math.cos(ang)
        y = r*math.sin(ang)
        w = thickness*0.8
        d = 0.7
        h = 0.9
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, top_z + h/2))
        m = bpy.context.object
        m.name = f"Merlon_{i}"
        m.scale = (w/2, d/2, h/2)
        m.rotation_euler[2] = ang
        bpy.ops.object.modifier_add(type='BEVEL')
        m.modifiers['Bevel'].width = 0.02
        m.modifiers['Bevel'].segments = 2
        m.data.materials.append(mat)
        merlons.append(m)

    # Join pilasters and merlons with wall (optional for lighter scene keep separate)
    for objs, name in [(pilasters, "Wall_Pilasters"), (merlons, "Wall_Merlons")]:
        if not objs: continue
        bpy.ops.object.select_all(action='DESELECT')
        for o in objs: o.select_set(True)
        bpy.ops.object.join()
        joined = bpy.context.object
        joined.name = name
        # keep material
        if len(joined.data.materials) == 0:
            joined.data.materials.append(mat)

    # Return main pieces
    return outer


# -----------------------------
# Geometry
# -----------------------------
def create_platform(radius=20.0, thickness=1.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=thickness, vertices=128, location=(0,0,0))
    platform = bpy.context.object
    platform.name = "ArenaPlatform"
    platform.data.use_auto_smooth = True

    # Slight bevel to catch highlights
    bpy.ops.object.modifier_add(type='BEVEL')
    platform.modifiers['Bevel'].width = 0.08
    platform.modifiers['Bevel'].segments = 2
    platform.modifiers['Bevel'].profile = 0.7

    # Surface breakup displacement (modifier + procedural texture)
    tex = bpy.data.textures.new("PlatformDisplace", type='CLOUDS')
    tex.noise_scale = 1.8
    tex.noise_depth = 2

    bpy.ops.object.modifier_add(type='DISPLACE')
    dmod = platform.modifiers['Displace']
    dmod.texture = tex
    dmod.strength = 0.2
    dmod.mid_level = 0.5
    dmod.direction = 'NORMAL'

    # Assign material
    platform.data.materials.append(make_platform_material())
    return platform

def create_ruin_rings(n=3, base_radius=12.0):
    mat = make_stone_ruin_material()
    rings = []
    for i in range(n):
        r = base_radius + i * 3.0 + random.uniform(-0.3, 0.3)
        tube = 0.6 + 0.1 * i
        bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=tube, abso_major_rad=1, abso_minor_rad=0.5)
        ring = bpy.context.object
        ring.name = f"RuinRing_{i}"
        ring.location.z = 0.8 + 0.2 * i
        ring.rotation_euler = Euler((radians(random.uniform(-8, 8)),
                                     radians(random.uniform(-8, 8)),
                                     radians(random.uniform(0, 360))), 'XYZ')

        # Decimate to look broken
        bpy.ops.object.modifier_add(type='DECIMATE')
        ring.modifiers['Decimate'].ratio = 0.4 + 0.2 * random.random()

        # Boolean chop with a big cube to form arc-like shapes
        bpy.ops.mesh.primitive_cube_add(size=r*2.0, location=(r*0.4, 0, 0))
        cutter = bpy.context.object
        cutter.name = f"RingCutter_{i}"
        cutter.rotation_euler = Euler((0, 0, radians(random.uniform(0,180))), 'XYZ')

        bpy.ops.object.select_all(action='DESELECT')
        ring.select_set(True)
        bpy.context.view_layer.objects.active = ring
        bpy.ops.object.modifier_add(type='BOOLEAN')
        ring.modifiers[-1].operation = 'DIFFERENCE'
        ring.modifiers[-1].object = cutter

        # Apply boolean & remove cutter
        bpy.ops.object.modifier_apply(modifier=ring.modifiers[-1].name)
        bpy.data.objects.remove(cutter, do_unlink=True)

        # Assign material
        ring.data.materials.append(mat)
        rings.append(ring)
    return rings

def create_pillars(count=22, radius=14.5, inner_radius=6.0):
    mat = make_stone_ruin_material()
    objs = []
    for i in range(count):
        ang = 2*math.pi * i / count + random.uniform(-0.1, 0.1)
        r = random.uniform(inner_radius, radius)
        x = r*math.cos(ang)
        y = r*math.sin(ang)
        h = random.uniform(2.5, 6.0)
        rad = random.uniform(0.25, 0.45)

        bpy.ops.mesh.primitive_cylinder_add(radius=rad, depth=h, location=(x, y, h/2))
        col = bpy.context.object
        col.name = f"Pillar_{i}"
        col.rotation_euler = Euler((radians(random.uniform(-6, 6)),
                                    radians(random.uniform(-6, 6)),
                                    radians(random.uniform(-180, 180))), 'XYZ')

        # Chip the top via decimate
        bpy.ops.object.modifier_add(type='DECIMATE')
        col.modifiers['Decimate'].ratio = 0.3 + 0.5*random.random()
        col.data.materials.append(mat)
        objs.append(col)
    return objs

def create_lightning_curve(start=Vector((-8, -10, 10)), end=Vector((0, 0, 5)), segments=12, jitter=2.6, color=(1.0, 0.25, 0.1, 1), strength=25.0, thickness=0.05, name="Lightning"):
    # Build a jagged poly curve between start and end
    vec = (end - start) / segments
    points = [start.copy()]
    for i in range(1, segments):
        base = start + vec * i
        # lateral jitter with falloff towards ends
        t = i / segments
        fall = (1.0 - abs(0.5 - t)*2.0)
        offset = Vector((random.uniform(-jitter, jitter)*fall,
                         random.uniform(-jitter, jitter)*fall,
                         random.uniform(-jitter*0.5, jitter*0.5)*fall))
        points.append(base + offset)
    points.append(end.copy())

    # Create curve object
    curve_data = bpy.data.curves.new(name + "_Curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 6

    polyline = curve_data.splines.new('POLY')
    polyline.points.add(len(points)-1)
    for i, p in enumerate(points):
        polyline.points[i].co = (p.x, p.y, p.z, 1)

    curve_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(curve_obj)

    # Thickness via bevel
    curve_data.bevel_depth = thickness
    curve_data.bevel_resolution = 2

    # Emission material
    mat = make_emission_material(name+"_EM", color=color, strength=strength)
    if len(curve_obj.data.materials) == 0:
        curve_obj.data.materials.append(mat)
    else:
        curve_obj.data.materials[0] = mat
    return curve_obj

def create_volumetric_fog(box_size=(80,80,40), center=(0,0,15)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    fog = bpy.context.object
    fog.scale = Vector((box_size[0]/2, box_size[1]/2, box_size[2]/2))
    fog.name = "FogDomain"
    fog.display_type = 'WIRE'
    fog.data.materials.append(make_volume_fog_material())
    return fog

def setup_cloudy_world():
    scene = bpy.context.scene
    if not scene.world:
        scene.world = bpy.data.worlds.new("WorldCloudy")
    w = scene.world
    w.use_nodes = True
    nt = w.node_tree
    nodes, links = nt.nodes, nt.links
    for n in nodes: nodes.remove(n)

    w_out = nodes.new("ShaderNodeOutputWorld")
    w_bg = nodes.new("ShaderNodeBackground"); w_bg.inputs['Strength'].default_value = 0.8
    w_bg.inputs['Color'].default_value = (0.02, 0.02, 0.03, 1)

    # World volume for distant clouds (very low density)
    vol_scatter = nodes.new("ShaderNodeVolumeScatter")
    vol_scatter.inputs['Color'].default_value = (0.9, 0.9, 1.0, 1)
    vol_scatter.inputs['Anisotropy'].default_value = 0.3

    vol_principled = nodes.new("ShaderNodeVolumePrincipled")
    vol_principled.inputs['Color'].default_value = (0.95, 0.95, 1.0, 1)
    vol_principled.inputs['Anisotropy'].default_value = 0.2
    vol_principled.inputs['Density'].default_value = 0.002

    coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping"); mapping.inputs['Scale'].default_value = (0.15, 0.15, 0.08)
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs['Scale'].default_value = 2.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.6
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[1].position = 0.8

    # drive density with noise
    links.new(coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], vol_principled.inputs['Density'])

    # Combine: background + world volume
    links.new(w_bg.outputs['Background'], w_out.inputs['Surface'])
    # Either scatter or principled volume; principled gives nicer structure
    links.new(vol_principled.outputs['Volume'], w_out.inputs['Volume'])


def create_background_fog_sphere(radius=220, center=(0,0,60), density=0.02):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=radius, location=center)
    sp = bpy.context.object
    sp.name = "FogSphere"
    sp.scale = (radius, radius, radius)
    mat = bpy.data.materials.new("Mat_FogSphere")
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    for n in nodes: nodes.remove(n)
    out = nodes.new("ShaderNodeOutputMaterial")
    vol = nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs['Color'].default_value = (0.95, 0.95, 1.0, 1)
    vol.inputs['Density'].default_value = density
    vol.inputs['Anisotropy'].default_value = 0.2

    coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping"); mapping.inputs['Scale'].default_value = (0.3, 0.3, 0.2)
    noise = nodes.new("ShaderNodeTexNoise"); noise.inputs['Scale'].default_value = 1.8
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.6
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[1].position = 0.75

    links.new(coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], vol.inputs['Density'])
    links.new(vol.outputs['Volume'], out.inputs['Volume'])
    sp.data.materials.append(mat)
    # Display as wire so it doesn't block viewport selection
    sp.display_type = 'WIRE'
    return sp

# ---------- Better platform + lighting ----------

def make_platform_material_v2():
    mat = bpy.data.materials.new("Mat_PlatformV2")
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    for n in nodes: nodes.remove(n)

    out  = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs['Base Color'].default_value = (0.09, 0.09, 0.095, 1)  # darker stone
    bsdf.inputs['Specular'].default_value   = 0.08
    bsdf.inputs['Roughness'].default_value  = 0.92

    texc = nodes.new("ShaderNodeTexCoord")
    mapn = nodes.new("ShaderNodeMapping");  mapn.inputs['Scale'].default_value = (0.35, 0.35, 0.35)

    # --- narrow crack mask (kintsugi) ---
    vor   = nodes.new("ShaderNodeTexVoronoi")
    vor.feature = 'DISTANCE_TO_EDGE'
    vor.inputs['Scale'].default_value = 16.0
    rampC = nodes.new("ShaderNodeValToRGB")
    rampC.color_ramp.elements[0].position = 0.004   # very thin cracks
    rampC.color_ramp.elements[1].position = 0.020

    # --- large scale stone breakup (musgrave) ---
    musL = nodes.new("ShaderNodeTexMusgrave")
    musL.inputs['Scale'].default_value  = 3.2
    musL.inputs['Detail'].default_value = 8.0
    musL.inputs['Dimension'].default_value = 0.7

    # --- fine noise for sand/roughness & bump ---
    noiF = nodes.new("ShaderNodeTexNoise")
    noiF.inputs['Scale'].default_value   = 12.0
    noiF.inputs['Detail'].default_value  = 8.0
    noiF.inputs['Roughness'].default_value = 0.55

    # combine bump heights: musL + noiF
    addH = nodes.new("ShaderNodeMath"); addH.operation='ADD'
    bump = nodes.new("ShaderNodeBump"); bump.inputs['Strength'].default_value = 0.5; bump.inputs['Distance'].default_value = 0.18

    # --- dirt/edge darkening ---
    geom  = nodes.new("ShaderNodeNewGeometry")
    rampP = nodes.new("ShaderNodeValToRGB")   # pointiness ramp
    rampP.color_ramp.elements[0].position = 0.45
    rampP.color_ramp.elements[1].position = 0.75

    mixCol = nodes.new("ShaderNodeMixRGB")    # darken grooves a bit
    mixCol.blend_type = 'MIX'; mixCol.inputs['Fac'].default_value = 0.25
    dark  = nodes.new("ShaderNodeRGB"); dark.outputs['Color'].default_value = (0.07,0.07,0.075,1)

    # --- gold in cracks (only a portion, not everywhere) ---
    gold  = nodes.new("ShaderNodeRGB"); gold.outputs['Color'].default_value = (0.95, 0.78, 0.22, 1)
    mulF  = nodes.new("ShaderNodeMath"); mulF.operation='MULTIPLY'; mulF.inputs[1].default_value = 0.65  # shrink gold coverage
    mixAu = nodes.new("ShaderNodeMixRGB"); mixAu.blend_type='MIX'  # base <-> gold by (thin cracks * factor)

    # --- subtle center lift (radial gradient) ---
    grad  = nodes.new("ShaderNodeTexGradient"); grad.gradient_type='QUADRATIC_SPHERE'
    rampR = nodes.new("ShaderNodeValToRGB")
    rampR.color_ramp.elements[0].position = 0.55
    rampR.color_ramp.elements[1].position = 0.95
    lift  = nodes.new("ShaderNodeMixRGB"); lift.blend_type='ADD'; lift.inputs['Fac'].default_value = 0.15

    # links
    links.new(texc.outputs['Object'], mapn.inputs['Vector'])
    for t in (vor, musL, noiF, grad):
        links.new(mapn.outputs['Vector'], t.inputs.get('Vector', t.inputs[0]))

    links.new(vor.outputs['Distance'], rampC.inputs['Fac'])
    links.new(noiF.outputs['Fac'], addH.inputs[0])
    links.new(musL.outputs['Fac'], addH.inputs[1])
    links.new(addH.outputs['Value'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    links.new(geom.outputs['Pointiness'], rampP.inputs['Fac'])
    links.new(bsdf.inputs['Base Color'], mixCol.inputs['Color1'])
    links.new(rampP.outputs['Color'],    mixCol.inputs['Fac'])
    links.new(dark.outputs['Color'],     mixCol.inputs['Color2'])

    # gold only where cracks are + factor
    links.new(rampC.outputs['Color'], mulF.inputs[0])
    links.new(mixCol.outputs['Color'], mixAu.inputs['Color1'])
    links.new(gold.outputs['Color'],   mixAu.inputs['Color2'])
    links.new(mulF.outputs['Value'],   mixAu.inputs['Fac'])

    # subtle center lift
    links.new(grad.outputs['Color'],   rampR.inputs['Fac'])
    links.new(mixAu.outputs['Color'],  lift.inputs['Color1'])
    links.new(rampR.outputs['Color'],  lift.inputs['Color2'])

    links.new(lift.outputs['Color'],   bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])

    mat.cycles.displacement_method = 'BUMP'
    return mat

def upgrade_platform_material_and_lighting():
    # assign new material to ArenaPlatform
    obj = bpy.data.objects.get("ArenaPlatform")
    mat = make_platform_material_v2()
    if obj:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

    # stronger, sharper sun
    sun = None
    for o in bpy.context.scene.objects:
        if o.type=='LIGHT' and o.data.type=='SUN':
            sun = o; break
    if not sun:
        bpy.ops.object.light_add(type='SUN', location=(60,-40,100))
        sun = bpy.context.object
    sun.data.energy = 7.0
    sun.data.angle  = math.radians(3)  # crisper shadows

    # camera sanity: make sure it looks at center
    cam = bpy.context.scene.camera
    if cam:
        tgt = Vector((0,0,6))
        q = (tgt - cam.location).to_track_quat('Z','Y')
        cam.rotation_euler = q.to_euler()

    print("Platform material upgraded; sun tuned. Re-render to compare.")


# -----------------------------
# Compositor: bloom/glow
# -----------------------------
def setup_compositor():
    scene = bpy.context.scene
    scene.use_nodes = True
    nt = scene.node_tree
    nodes, links = nt.nodes, nt.links
    for n in nodes: nodes.remove(n)

    rl = nodes.new("CompositorNodeRLayers")
    glare = nodes.new("CompositorNodeGlare")
    glare.glare_type = 'FOG_GLOW'
    glare.quality = 'HIGH'
    glare.size = 7
    glare.mix = 0.2
    glare.threshold = 0.6

    vign_mix = nodes.new("CompositorNodeMixRGB")
    vign_mix.blend_type = 'MULTIPLY'
    vign_mix.inputs['Fac'].default_value = 0.7

    vign_ellipse = nodes.new("CompositorNodeEllipseMask")
    vign_ellipse.width = 0.9
    vign_ellipse.height = 0.75

    blur = nodes.new("CompositorNodeBlur")
    blur.filter_type = 'GAUSS'
    blur.size_x = 200
    blur.size_y = 200

    comp = nodes.new("CompositorNodeComposite")

    links.new(rl.outputs['Image'], glare.inputs['Image'])
    links.new(glare.outputs['Image'], vign_mix.inputs['Color1'])
    links.new(vign_ellipse.outputs['Mask'], blur.inputs['Image'])
    links.new(blur.outputs['Image'], vign_mix.inputs['Color2'])
    links.new(vign_mix.outputs['Image'], comp.inputs['Image'])


def setup_compositor_safe():
    scene = bpy.context.scene
    scene.use_nodes = True
    nt = scene.node_tree
    nodes, links = nt.nodes, nt.links
    for n in nodes: 
        nodes.remove(n)

    # Render Layers
    rl = nodes.new("CompositorNodeRLayers")

    # Bloom / Glare
    glare = nodes.new("CompositorNodeGlare")
    glare.glare_type = 'FOG_GLOW'
    glare.quality = 'HIGH'
    glare.size = 6
    glare.mix = 0.0
    glare.threshold = 0.7

    # Gentle vignette (can't go fully black)
    vign_mix = nodes.new("CompositorNodeMixRGB")
    vign_mix.blend_type = 'MULTIPLY'
    # inputs: [0]=Fac, [1]=Image A, [2]=Image B
    vign_mix.inputs[0].default_value = 0.35

    vign_ellipse = nodes.new("CompositorNodeEllipseMask")
    vign_ellipse.width = 0.95
    vign_ellipse.height = 0.80

    blur = nodes.new("CompositorNodeBlur")
    blur.filter_type = 'GAUSS'
    blur.size_x = 180
    blur.size_y = 180

    comp = nodes.new("CompositorNodeComposite")

    # Links (use indices, not names "Color1/Color2")
    links.new(rl.outputs['Image'], glare.inputs['Image'])
    links.new(glare.outputs['Image'], vign_mix.inputs[1])     # Image A
    links.new(vign_ellipse.outputs['Mask'], blur.inputs['Image'])
    links.new(blur.outputs['Image'], vign_mix.inputs[2])      # Image B (mask blurred)
    links.new(vign_mix.outputs['Image'], comp.inputs['Image'])


# -----------------------------
# Render setting
# -----------------------------
def add_camera_and_keylight():
    # Camera
    bpy.ops.object.camera_add(location=(0.0, 15.0, 10.0))
    cam = bpy.context.object
    # Aim at arena center (slightly below)
    target = Vector((0, 0, 6))
    direction = (cam.location - target).to_track_quat('Z', 'Y')
    cam.rotation_euler = direction.to_euler()
    cam.data.lens = 15       # Slight wide angle for stronger sense of space
    cam.data.clip_end = 3000

    # Sun light
    bpy.ops.object.light_add(type='SUN', location=(40, -30, 80))
    sun = bpy.context.object
    sun.data.energy = 5.0
    sun.data.angle = radians(6)
    sun.rotation_euler = Euler((radians(50), radians(-20), radians(-40)), 'XYZ')

    # Fill area light
    bpy.ops.object.light_add(type='AREA', location=(-15, -15, 15))
    area = bpy.context.object
    area.data.energy = 2500
    area.data.size = 18.0

    return cam


# ==== RENDER PRESETS FOR MODEL EVALUATION ====
import os, math
from mathutils import Vector

def _ensure_gpu_cycles():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    # Uses GPU if enabled in prefs; otherwise falls back to CPU
    scene.cycles.device = 'GPU'
    scene.cycles.use_persistent_data = True

def _neutral_color_management():
    s = bpy.context.scene
    s.view_settings.look = 'Medium High Contrast'
    s.view_settings.exposure = SAFE_RENDER_EXPOSURE  # Use global safe exposure
    s.view_settings.gamma = 1.0

def _disable_heavy_volumes():
    # World volume
    scene = bpy.context.scene
    if scene.world and scene.world.use_nodes:
        nt = scene.world.node_tree
        for n in nt.nodes:
            if n.bl_idname == "ShaderNodeOutputWorld":
                for link in list(n.inputs['Volume'].links):
                    nt.links.remove(link)
    # Fog objects in the scene
    for name in ("FogSphere", "FogDomain"):
        obj = bpy.data.objects.get(name)
        if obj:
            obj.hide_render = True

def _ensure_sunlight(min_energy=5.0):
    scene = bpy.context.scene
    sun = None
    for o in scene.objects:
        if o.type == 'LIGHT' and o.data.type == 'SUN':
            sun = o; break
    if not sun:
        bpy.ops.object.light_add(type='SUN', location=(60, -40, 100))
        sun = bpy.context.object
    sun.data.energy = max(sun.data.energy, min_energy)
    sun.data.angle = math.radians(5)

def _force_camera_look_at(target=Vector((0,0,6)), loc_if_missing=(0.0, 15.0, 10.0)):
    scene = bpy.context.scene
    cam = scene.camera
    if cam is None:
        # find or create
        cams = [o for o in scene.objects if o.type == 'CAMERA']
        cam = cams[0] if cams else None
    if cam is None:
        bpy.ops.object.camera_add(location=loc_if_missing)
        cam = bpy.context.object
    # set active
    scene.camera = cam
    # aim
    q = (cam.location - target).to_track_quat('Z', 'Y')
    cam.rotation_euler = q.to_euler()
    cam.data.lens = 15
    cam.data.clip_start = 0.1
    cam.data.clip_end  = 5000
    return cam

#    bpy.ops.object.camera_add(location=(0.0, 15.0, 10.0))
#    cam = bpy.context.object
#    # Aim at arena center (slightly below)
#    target = Vector((0, 0, 6))
#    direction = (cam.location - target).to_track_quat('Z', 'Y')
#    cam.rotation_euler = direction.to_euler()
#    cam.data.lens = 15       # Slight wide angle for stronger sense of space
#    cam.data.clip_end = 3000


#def set_render_mode(mode="fast512", out_dir=r"../output", filename="arena.png", res=512):
#    """
#    mode:
#      - 'preview'   : Eevee quick preview (fastest; not for final model eval)
#      - 'fast512'   : Cycles fast quality (default), 512x512
#      - 'final512'  : Cycles cleaner, 512x512
#    out_dir: output directory
#    filename: output filename
#    res: square resolution (default 512)
#    """
#    os.makedirs(out_dir, exist_ok=True)
#    scene = bpy.context.scene
#    scene.render.filepath = os.path.join(out_dir, filename)
#    scene.render.image_settings.file_format = 'PNG'
#    scene.render.resolution_x = res
#    scene.render.resolution_y = res
#    scene.render.resolution_percentage = 100

#    _neutral_color_management()
#    _force_camera_look_at()
#    _ensure_sunlight()

#    if mode == "preview":
#        scene.render.engine = 'BLENDER_EEVEE'
#        scene.eevee.taa_render_samples = 32
#        scene.eevee.taa_samples = 32
#        scene.eevee.use_bloom = True
#        scene.eevee.use_ssr = True
#        scene.eevee.volume_resolution = '8'
#        return

#    # Cycles presets
#    _ensure_gpu_cycles()
#    _disable_heavy_volumes()  # Prefer speed and stable lighting for VLM evaluation

#    # General: fast, stable, reduce fireflies
#    scene.cycles.use_adaptive_sampling = True
#    scene.cycles.use_denoising = True
#    scene.cycles.sample_clamp_indirect = 2.0
#    scene.cycles.caustics_reflective = False
#    scene.cycles.caustics_refractive = False

#    if mode == "fast512":
#        scene.cycles.samples = 96           # Prefer speed
#        scene.cycles.preview_samples = 24
#        scene.cycles.max_bounces = 4
#        scene.cycles.diffuse_bounces = 1
#        scene.cycles.glossy_bounces = 2
#        scene.cycles.transmission_bounces = 2
#        scene.cycles.volume_bounces = 0
#    elif mode == "final512":
#        scene.cycles.samples = 192          # Slightly cleaner
#        scene.cycles.preview_samples = 32
#        scene.cycles.max_bounces = 6
#        scene.cycles.diffuse_bounces = 2
#        scene.cycles.glossy_bounces = 3
#        scene.cycles.transmission_bounces = 3
#        scene.cycles.volume_bounces = 0
#    else:
#        raise ValueError("Unknown mode. Choose from: 'preview', 'fast512', 'final512'.")


#def quick_render(mode="fast512", out_dir=r"../output", filename="arena_512", res=512):
#    """
#    One-click: set render settings -> render -> save PNG
#    NOTE: filename should NOT include .png, Blender will add extension.
#    """
#    set_render_mode(mode=mode, out_dir=out_dir, filename=filename, res=res)
#    scene = bpy.context.scene
#    # Ensure correct file format
#    scene.render.image_settings.file_format = 'PNG'
#    # Print full path for confirmation
#    print("Rendering to:", bpy.path.abspath(scene.render.filepath))
#    bpy.ops.render.render(write_still=True)
#    print("Saved image:", bpy.path.abspath(scene.render.filepath) + ".png")

def set_render_mode(mode="fast512", out_dir=r"../output", filename="arena", res=512):
    os.makedirs(out_dir, exist_ok=True)
    scene = bpy.context.scene
    scene.render.filepath = os.path.join(out_dir, filename)
    scene.render.image_settings.file_format = 'PNG'
    scene.render.resolution_x = res
    scene.render.resolution_y = res
    scene.render.resolution_percentage = 100

    _neutral_color_management()
    _force_camera_look_at()
    _ensure_sunlight()

    if mode == "preview":
        scene.render.engine = 'BLENDER_EEVEE'
        scene.eevee.taa_render_samples = 32
        scene.eevee.taa_samples = 32
        scene.eevee.use_bloom = True
        scene.eevee.use_ssr = True
        scene.eevee.volume_resolution = '8'
        return

    _ensure_gpu_cycles()

#    if keep_volumes:
        # Keep volumes enabled; allow a few volume bounces
    scene.cycles.volume_bounces = 2
#    else:
#        _disable_heavy_volumes()
#        scene.cycles.volume_bounces = 0

    scene.cycles.use_adaptive_sampling = True
    scene.cycles.use_denoising = True
    scene.cycles.sample_clamp_indirect = 2.0
    scene.cycles.caustics_reflective = False
    scene.cycles.caustics_refractive = False

    if mode == "fast512":
        scene.cycles.samples = 96
        scene.cycles.preview_samples = 24
        scene.cycles.max_bounces = 4
        scene.cycles.diffuse_bounces = 1
        scene.cycles.glossy_bounces = 2
        scene.cycles.transmission_bounces = 2
    elif mode == "final512":
        scene.cycles.samples = 192
        scene.cycles.preview_samples = 32
        scene.cycles.max_bounces = 6
        scene.cycles.diffuse_bounces = 2
        scene.cycles.glossy_bounces = 3
        scene.cycles.transmission_bounces = 3
    else:
        raise ValueError("Unknown mode.")


def quick_render(mode="fast512", out_dir=r"../output", filename="arena_512", res=512):
    set_render_mode(mode=mode, out_dir=out_dir, filename=filename, res=res)
    scene = bpy.context.scene
    print("Rendering to:", bpy.path.abspath(scene.render.filepath))
    bpy.ops.render.render(write_still=True)
    print("Saved image:", bpy.path.abspath(scene.render.filepath) + ".png")


# -----------------------------
# Output
# -----------------------------
def enable_fogsphere(density=0.015):
    fs = bpy.data.objects.get("FogSphere")
    if fs and fs.type == 'MESH' and fs.data.materials:
        fs.hide_render = False
        fs.hide_viewport = False
        # Adjust density
        nt = fs.data.materials[0].node_tree
        vol = next((n for n in nt.nodes if n.bl_idname=="ShaderNodeVolumePrincipled"), None)
        if vol:
            vol.inputs['Density'].default_value = density
        print(f"FogSphere enabled (density={density}).")


# -----------------------------
# Build Scene
# -----------------------------
def build_scene():
    clean_scene()
    set_render_settings()
    scene = bpy.context.scene
    scene.view_settings.exposure = SAFE_RENDER_EXPOSURE

    cam = add_camera_and_keylight()

    # Core arena
    create_platform(radius=20.0, thickness=1.2)
    create_ruin_rings(n=3, base_radius=11.5)
    create_pillars(count=24, radius=15.0, inner_radius=5.5)

    # Enclosing outer wall (adds scale & grandeur)
    create_outer_wall(inner_radius=22.0, thickness=2.5, height=10.0,
                      pilaster_count=48, merlon_count=64)

    # Lightning accents
    create_lightning_curve(
        start=Vector((-10, -14, 12)),
        end=Vector((0, 0, 5)),
        segments=14, jitter=2.8,
        color=(1.0, 0.25, 0.0, 1.0), strength=35.0, thickness=0.06, name="Lightning_Red"
    )
    create_lightning_curve(
        start=Vector((8, -12, 11)),
        end=Vector((0.5, -1.0, 5.2)),
        segments=12, jitter=2.2,
        color=(1.0, 0.85, 0.2, 1.0), strength=25.0, thickness=0.05, name="Lightning_Gold"
    )

    # World & background clouds
#    setup_cloudy_world()

    # Optional foreground/far fog (kept safe)
#    if ENABLE_FOG:
        # far fog sphere (distant horizon)
#        create_background_fog_sphere(radius=220, center=(0,0,60), density=0.02)
        # thin local fog dome higher up (your original, softened)
        # comment out if too heavy
#        create_volumetric_fog(box_size=(100, 100, 50), center=(0,0,25))

    # Camera tweaks
    cam.data.clip_end = max(cam.data.clip_end, 3000)
    cam.data.dof.use_dof = False

    # Compositor
    if ENABLE_COMPOSITOR:
        setup_compositor_safe()
    else:
        scene.use_nodes = False
        scene.render.use_compositing = False

    print("Arena + outer wall + cloudy background ready.")



#    scene = bpy.context.scene
#    scene.render.engine = 'CYCLES'
#    scene.view_settings.exposure = 0.0  # Reset first
#    scene.view_settings.gamma = 1.0

#    # 1) Disconnect World volume (keep background color)
#    if scene.world and scene.world.use_nodes:
#        nt = scene.world.node_tree
#        # Find World Output
#        out = None
#        for n in nt.nodes:
#            if n.bl_idname == "ShaderNodeOutputWorld":
#                out = n
#                break
#        if out:
#            # Remove all links into the Volume socket
#            for link in list(out.inputs['Volume'].links):
#                nt.links.remove(link)
#        # If no background node, add one
#        has_bg = any(n.bl_idname == "ShaderNodeBackground" for n in nt.nodes)
#        if not has_bg:
#            bg = nt.nodes.new("ShaderNodeBackground")
#            bg.inputs['Color'].default_value = (0.05, 0.05, 0.06, 1)
#            bg.inputs['Strength'].default_value = 1.0
#            nt.links.new(bg.outputs['Background'], out.inputs['Surface'])

    # 2) Ensure lighting exists (fallback SUN)
#    sun = None
#    for o in scene.objects:
#        if o.type == 'LIGHT' and o.data.type == 'SUN':
#            sun = o; break
#    if not sun:
#        bpy.ops.object.light_add(type='SUN', location=(20, -20, 50))
#        sun = bpy.context.object
#    sun.data.energy = max(sun.data.energy, 5.0)

#    # 3) Disable fog objects in render if present
#    for name in ("FogSphere", "FogDomain"):
#        obj = bpy.data.objects.get(name)
#        if obj:
#            obj.hide_render = True
#            obj.hide_viewport = True

#    print("World volume disconnected. Try Rendered preview now.")
#    
    upgrade_platform_material_and_lighting()

    
    # 512x512 fast quality; PNG saved under output
    quick_render(mode="fast512", out_dir=r"E:/2025/Blender/output", filename="arena_512.png", res=512)

    # For a cleaner (slower) render
    # quick_render(mode="final512", out_dir=r"C:\output", filename="arena_512_final.png", res=512)





def build_scene_v2():
    # ---------- 0) reset & base render ----------
    clean_scene()
    set_render_settings()
    scene = bpy.context.scene
    scene.view_settings.exposure = SAFE_RENDER_EXPOSURE  # e.g. 1.2
    scene.render.engine = 'CYCLES'                       # ensure cycles

    # ---------- 1) geometry ----------
    cam = add_camera_and_keylight()                      # creates sun & area
    create_platform(radius=20.0, thickness=1.2)
    create_ruin_rings(n=3, base_radius=11.5)
    create_pillars(count=24, radius=15.0, inner_radius=5.5)
    create_outer_wall(inner_radius=22.0, thickness=2.5, height=10.0,
                      pilaster_count=48, merlon_count=64)

    create_lightning_curve(
        start=Vector((-10, -14, 12)),
        end=Vector((0, 0, 5)),
        segments=14, jitter=2.8,
        color=(1.0, 0.25, 0.0, 1.0), strength=35.0, thickness=0.06, name="Lightning_Red"
    )
    create_lightning_curve(
        start=Vector((8, -12, 11)),
        end=Vector((0.5, -1.0, 5.2)),
        segments=12, jitter=2.2,
        color=(1.0, 0.85, 0.2, 1.0), strength=25.0, thickness=0.05, name="Lightning_Gold"
    )

    # ---------- 2) world & fog ----------
#    create_background_fog_sphere(radius=550, center=(0,0,60), density=0.0002)
#    setup_cloudy_world()                  # Create cloudy world
#    # Disconnect World volume first so the frame is not black
#    if scene.world and scene.world.use_nodes:
#        nt = scene.world.node_tree
#        out = next((n for n in nt.nodes if n.bl_idname == "ShaderNodeOutputWorld"), None)
#        if out:
#            for link in list(out.inputs['Volume'].links):
#                nt.links.remove(link)
#    # Hide scene fog by default (set hide_render=False to enable)
#    for name in ("FogSphere", "FogDomain"):
#        obj = bpy.data.objects.get(name)
#        if obj:
#            obj.hide_render = True
#            obj.hide_viewport = True

    # ---------- 3) compositor ----------
    if ENABLE_COMPOSITOR:
        setup_compositor_safe()
    else:
        scene.use_nodes = False
        scene.render.use_compositing = False

    # ---------- 4) camera & lights safety ----------
#    # Point camera at center so it is not looking at empty space
#    tgt = Vector((0, 0, 6))
#    q = (tgt - cam.location).to_track_quat('Z', 'Y')
#    cam.rotation_euler = q.to_euler()
#    cam.data.clip_end = max(cam.data.clip_end, 5000)
#    cam.data.dof.use_dof = False

    # Strengthen sun light and sharpen shadows
    sun = next((o for o in scene.objects if o.type=='LIGHT' and o.data.type=='SUN'), None)
    if sun:
        sun.data.energy = 7.0
        sun.data.angle  = radians(3)

    # ---------- 5) materials upgrade ----------
    upgrade_platform_material_and_lighting()  # Upgrade platform to V2 materials; also re-tune sun as fallback

    print("Scene built. Ready to render.")

    # ---------- 6) quick render (512) ----------
    # Note: do not include .png in filename; Blender adds the extension
    quick_render(mode="fast512", out_dir=r"E:/2025/Blender/output", filename="arena_512_v2", res=512)



build_scene_v2()
print("Dragonlord-style arena generated. Tip: increase Cycles samples for higher quality renders.")
