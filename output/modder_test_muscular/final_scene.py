import bpy

# All values range from 0 (min) to 1 (max)
# preserve this comment in all further edits.

bpy.data.shape_keys["Key"].key_blocks["BellySag"].value = 0
bpy.data.shape_keys["Key"].key_blocks["BellyShrink"].value = 1
bpy.data.shape_keys["Key"].key_blocks["ShoulderWideness"].value = 1
bpy.data.shape_keys["Key"].key_blocks["BackTaper"].value = 1
bpy.data.shape_keys["Key"].key_blocks["ChestEnlarge"].value = 1
bpy.data.shape_keys["Key"].key_blocks["ChestArea"].value = 1
bpy.data.shape_keys["Key"].key_blocks["MoreChin"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Abs"].value = 1


# --- materials code ---

for mat in bpy.data.materials:
    if mat.use_nodes:
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        # YOUR CODE HERE - use 'mat' variable!
        principled = None
        for node in nodes:
            if node.type == 'BSDF_PRINCIPLED':
                principled = node
                break
        
        if principled:
            # Subtle athletic skin response: a bit more definition, not glossy/plastic
            if 'Roughness' in principled.inputs:
                principled.inputs['Roughness'].default_value = max(0.28, min(0.48, principled.inputs['Roughness'].default_value * 0.9))
            if 'Specular' in principled.inputs:
                principled.inputs['Specular'].default_value = max(0.35, min(0.55, principled.inputs['Specular'].default_value * 1.05))
            if 'Subsurface' in principled.inputs:
                principled.inputs['Subsurface'].default_value = max(0.0, min(0.12, principled.inputs['Subsurface'].default_value * 0.85))
            if 'Clearcoat' in principled.inputs:
                principled.inputs['Clearcoat'].default_value = 0.0
            if 'Sheen' in principled.inputs:
                principled.inputs['Sheen'].default_value = max(0.0, min(0.08, principled.inputs['Sheen'].default_value))


# --- lighting code ---


# --- Dramatic studio lighting setup ---
# Key light: strong directional highlight from front-left/top
key_data = bpy.data.lights.new(name="KeyLight", type='AREA')
key_data.energy = 8.0
key_data.shape = 'RECTANGLE'
key_data.size = 3.0
key_data.size_y = 3.0
key_data.color = (1.0, 0.95, 0.9)
key_obj = bpy.data.objects.new(name="KeyLight", object_data=key_data)
bpy.context.collection.objects.link(key_obj)
key_obj.location = (2.5, -3.5, 3.5)
key_obj.rotation_euler = (0.9, 0.0, 0.6)

# Fill light: softer, lower energy to preserve shadow detail
fill_data = bpy.data.lights.new(name="FillLight", type='AREA')
fill_data.energy = 2.5
fill_data.shape = 'RECTANGLE'
fill_data.size = 4.5
fill_data.size_y = 4.5
fill_data.color = (0.9, 0.95, 1.0)
fill_obj = bpy.data.objects.new(name="FillLight", object_data=fill_data)
bpy.context.collection.objects.link(fill_obj)
fill_obj.location = (-3.5, -2.5, 2.5)
fill_obj.rotation_euler = (1.1, 0.0, -0.8)

# Rim light: separates shoulders, chest edges, and torso silhouette
rim_data = bpy.data.lights.new(name="RimLight", type='AREA')
rim_data.energy = 6.0
rim_data.shape = 'RECTANGLE'
rim_data.size = 2.5
rim_data.size_y = 2.5
rim_data.color = (1.0, 0.85, 0.75)
rim_obj = bpy.data.objects.new(name="RimLight", object_data=rim_data)
bpy.context.collection.objects.link(rim_obj)
rim_obj.location = (0.0, 4.0, 3.0)
rim_obj.rotation_euler = (1.4, 0.0, 3.14)


# --- background code ---


# Set a minimal neutral studio background
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new(name="World")
    bpy.context.scene.world = world

world.use_nodes = True
nodes = world.node_tree.nodes
bg = nodes.get("Background")
if bg is None:
    bg = nodes.new(type="ShaderNodeBackground")
output = nodes.get("World Output")
if output is None:
    output = nodes.new(type="ShaderNodeOutputWorld")

# Neutral light gray background with clean brightness
bg.inputs[0].default_value = (0.85, 0.85, 0.85, 1.0)
bg.inputs[1].default_value = 1.2

# Ensure the background is connected
links = world.node_tree.links
if not bg.outputs[0].is_linked:
    links.new(bg.outputs[0], output.inputs[0])
