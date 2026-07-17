import bpy

# All values range from 0 (min) to 1 (max)
# preserve this comment in all further edits.

bpy.data.shape_keys["Key"].key_blocks["BellySag"].value = 0
bpy.data.shape_keys["Key"].key_blocks["BellyShrink"].value = 0
bpy.data.shape_keys["Key"].key_blocks["ShoulderWideness"].value = 1
bpy.data.shape_keys["Key"].key_blocks["BackTaper"].value = 1
bpy.data.shape_keys["Key"].key_blocks["ChestEnlarge"].value = 1
bpy.data.shape_keys["Key"].key_blocks["ChestArea"].value = 1
bpy.data.shape_keys["Key"].key_blocks["MoreChin"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Abs"].value = 1


# --- AI AGENT MODIFICATIONS ---

# --- Start materials ---
try:
    for mat in bpy.data.materials:
        if mat.use_nodes:
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            # YOUR CODE HERE - use 'mat' variable!
            for node in nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    # Cleaner, more polished skin look with subtle definition
                    if 'Roughness' in node.inputs:
                        node.inputs['Roughness'].default_value = max(0.18, node.inputs['Roughness'].default_value * 0.75)
                    if 'Specular' in node.inputs:
                        node.inputs['Specular'].default_value = min(0.55, max(node.inputs['Specular'].default_value, 0.42))
                    if 'Subsurface' in node.inputs:
                        node.inputs['Subsurface'].default_value = min(0.08, max(node.inputs['Subsurface'].default_value, 0.03))
                    if 'Subsurface Color' in node.inputs:
                        node.inputs['Subsurface Color'].default_value = (0.86, 0.62, 0.52, 1.0)
                    if 'Base Color' in node.inputs:
                        c = node.inputs['Base Color'].default_value
                        node.inputs['Base Color'].default_value = (min(1.0, c[0] * 1.03), min(1.0, c[1] * 1.01), min(1.0, c[2] * 0.99), c[3])
except Exception as e:
    print(f'![Agent materials Error]: {e}')
# --- End materials ---


# --- Start lighting ---
try:

    # Studio lighting setup for sculpted muscle definition
    import bpy

    # Key light: strong but controlled
    key_data = bpy.data.lights.new(name="StudioKey", type='AREA')
    key_data.energy = 1200
    key_data.shape = 'RECTANGLE'
    key_data.size = 3.0
    key_data.size_y = 2.0
    key_obj = bpy.data.objects.new(name="StudioKey", object_data=key_data)
    bpy.context.collection.objects.link(key_obj)
    key_obj.location = (2.5, -2.5, 3.0)
    key_obj.rotation_euler = (0.9, 0.0, 0.8)

    # Fill light: softer, lower intensity to preserve shadows
    fill_data = bpy.data.lights.new(name="StudioFill", type='AREA')
    fill_data.energy = 350
    fill_data.shape = 'RECTANGLE'
    fill_data.size = 4.0
    fill_data.size_y = 3.0
    fill_obj = bpy.data.objects.new(name="StudioFill", object_data=fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (-3.0, -1.5, 2.0)
    fill_obj.rotation_euler = (1.1, 0.0, -1.0)

    # Rim light: adds contour separation and highlights arms/shoulders
    rim_data = bpy.data.lights.new(name="StudioRim", type='AREA')
    rim_data.energy = 700
    rim_data.shape = 'RECTANGLE'
    rim_data.size = 2.5
    rim_data.size_y = 1.0
    rim_data.color = (0.85, 0.92, 1.0)
    rim_obj = bpy.data.objects.new(name="StudioRim", object_data=rim_data)
    bpy.context.collection.objects.link(rim_obj)
    rim_obj.location = (0.0, 3.0, 2.8)
    rim_obj.rotation_euler = (1.2, 0.0, 3.14)

    # Optional subtle world darkening for stronger contrast
    if bpy.context.scene.world and bpy.context.scene.world.use_nodes:
        bg = bpy.context.scene.world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs[1].default_value = 0.2
except Exception as e:
    print(f'![Agent lighting Error]: {e}')
# --- End lighting ---


# --- Start background ---
try:

    # Simple, uncluttered background for a fitness-portrait look
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    world.use_nodes = True
    nodes = world.node_tree.nodes
    bg = nodes.get("Background")
    if bg is None:
        bg = nodes.new(type="ShaderNodeBackground")
    output = nodes.get("World Output")
    if output is None:
        output = nodes.new(type="ShaderNodeOutputWorld")

    # Clean neutral backdrop
    bg.inputs[0].default_value = (0.92, 0.92, 0.92, 1.0)
    bg.inputs[1].default_value = 0.8
except Exception as e:
    print(f'![Agent background Error]: {e}')
# --- End background ---
