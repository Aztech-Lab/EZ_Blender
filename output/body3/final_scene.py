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
        for node in nodes:
            if node.type == 'BSDF_PRINCIPLED':
                if 'Roughness' in node.inputs:
                    node.inputs['Roughness'].default_value = max(0.0, min(1.0, node.inputs['Roughness'].default_value * 0.75))
                if 'Specular' in node.inputs:
                    node.inputs['Specular'].default_value = max(0.0, min(1.0, node.inputs['Specular'].default_value + 0.08))
                if 'Clearcoat' in node.inputs:
                    node.inputs['Clearcoat'].default_value = max(0.0, min(1.0, node.inputs['Clearcoat'].default_value + 0.05))
                if 'Clearcoat Roughness' in node.inputs:
                    node.inputs['Clearcoat Roughness'].default_value = max(0.0, min(1.0, node.inputs['Clearcoat Roughness'].default_value * 0.7))


# --- lighting code ---


# Studio lighting setup for muscle definition
# Key light: strong angled source to create clear highlights and shadows
key_light_data = bpy.data.lights.new(name="StudioKey", type='AREA')
key_light_data.energy = 1200
key_light_data.shape = 'RECTANGLE'
key_light_data.size = 2.5
key_light_data.size_y = 1.5
key_light = bpy.data.objects.new(name="StudioKey", object_data=key_light_data)
bpy.context.collection.objects.link(key_light)
key_light.location = (2.5, -3.5, 3.0)
key_light.rotation_euler = (0.9, 0.0, 0.7)

# Fill light: softer and lower energy to retain detail without flattening
fill_light_data = bpy.data.lights.new(name="StudioFill", type='AREA')
fill_light_data.energy = 350
fill_light_data.shape = 'RECTANGLE'
fill_light_data.size = 3.5
fill_light_data.size_y = 2.0
fill_light = bpy.data.objects.new(name="StudioFill", object_data=fill_light_data)
bpy.context.collection.objects.link(fill_light)
fill_light.location = (-3.0, -2.5, 2.2)
fill_light.rotation_euler = (1.1, 0.0, -0.8)

# Rim light: adds separation and emphasizes shoulder/arm edges
rim_light_data = bpy.data.lights.new(name="StudioRim", type='AREA')
rim_light_data.energy = 800
rim_light_data.shape = 'RECTANGLE'
rim_light_data.size = 1.5
rim_light_data.size_y = 1.0
rim_light = bpy.data.objects.new(name="StudioRim", object_data=rim_light_data)
bpy.context.collection.objects.link(rim_light)
rim_light.location = (0.0, 3.0, 2.8)
rim_light.rotation_euler = (1.4, 0.0, 3.14)

# Optional subtle world dimming for better contrast
if bpy.context.scene.world and bpy.context.scene.world.use_nodes:
    bg = bpy.context.scene.world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs[1].default_value = 0.25


# --- background code ---


# Make the background simple and studio-like
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world

world.use_nodes = True
nodes = world.node_tree.nodes
bg_node = nodes.get("Background")
if bg_node is None:
    bg_node = nodes.new(type="ShaderNodeBackground")

# Neutral light gray background for a clean studio look
bg_node.inputs[0].default_value = (0.95, 0.95, 0.95, 1.0)
bg_node.inputs[1].default_value = 0.8
