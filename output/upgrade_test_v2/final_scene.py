import bpy

# setting the strength of the HDR to be 0.9, which is strong. Decrease if you want less environment light coming in.
# for darker scenes, set this to 0.05. (like night scenes, with scenes with darker backgrounds)
# do not exceed 1.0 for this value.
bpy.data.worlds["World.001"].node_tree.nodes["HDRIHandler_ShaderNodeBackground"].inputs[1].default_value = 0.75
# NOTE: for darker scenes, make sure that the energy values below of each light is also low -- otherwise everything
# will be too bright.

# Area light 1: light from the right hand side
area_light_data = bpy.data.lights.new('light', type="AREA")
area_light = bpy.data.objects.new("Area",  area_light_data)
area_light.location = (0.7558, -0.2978, 0.2950 ) # (x,y, z)
area_light.scale = (0.4320, 0.1758, 0.4320) # (scale_x, scale_y, scale_z)
area_light.rotation_euler = (0.7196, 1.5708, 0) # (radians_x, radians_y, radians_z)
area_light.data.energy = 12.73 # keep this below 15.
area_light.data.color = (0.95, 1.0, 0.95) # (R, G, B )
area_light.data.shape = "SQUARE"
area_light.data.size = 1.0
area_light.data.shadow_soft_size = 3.14
bpy.context.collection.objects.link(area_light)

# Area light 2: Light reflecting off the back wall
area_light001_data = bpy.data.lights.new('light', type="AREA")
area_light001 = bpy.data.objects.new("Area.001",  area_light001_data)
area_light001.location = (-0.4267, 0.3767, 0.4435) # (x,y, z)
area_light001.scale = (0.6872, 0.6872, 0.6872) # (scale_x, scale_y, scale_z)
area_light001.rotation_euler = (1.1453, -0.0616, -0.0223) # (radians_x, radians_y, radians_z)
area_light001.data.energy = 12.73 # keep this below 15
area_light001.data.color = (0.95, 1.0, 0.95) # (R, G, B )
area_light001.data.shape = "SQUARE"
area_light001.data.size = 1.0
area_light001.data.shadow_soft_size = 3.14
bpy.context.collection.objects.link(area_light001)

# Area light 3: Light on the left hand side
area_light002_data = bpy.data.lights.new('light', type="AREA")
area_light002 = bpy.data.objects.new("Area.002",  area_light002_data)
area_light002.location = (-0.3151, -0.4322, 0.3610) # (x,y, z)
area_light002.scale = (1.0, 1.0 , 1.0 ) # (scale_x, scale_y, scale_z)
area_light002.rotation_euler = (1.2139, 0.0966, -0.6434)  # (radians_x, radians_y, radians_z)
area_light002.data.energy = 1.27 # keep this below 15
area_light002.data.color = (0.35, 1.0, 0.45) # neon-green tint
area_light002.data.shape = "SQUARE"
area_light002.data.size = 0.46
area_light002.data.shadow_soft_size = 3.14
bpy.context.collection.objects.link(area_light002)

# Area light 4: Light coming straight down from the top
area_light003_data = bpy.data.lights.new('light', type="AREA")
area_light003 = bpy.data.objects.new("Area.003",  area_light003_data)
area_light003.location = (0.0000, 0.0000, 1.1032) # (x,y, z)
area_light003.scale = (1.0, 1.0 , 1.0 ) # (scale_x, scale_y, scale_z)
area_light003.rotation_euler = (0, 0, 0)  # (radians_x, radians_y, radians_z)
area_light003.data.energy = 8.91  # keep this below 15
area_light003.data.color = (0.95, 1.0, 0.95) # (R, G, B )
area_light003.data.shape = "SQUARE"
area_light003.data.size = 1.0
area_light003.data.shadow_soft_size = 3.14
bpy.context.collection.objects.link(area_light003)

# Point light 1: Slightly behind the lotion.
point_light_data = bpy.data.lights.new('light', type="POINT")
point_light = bpy.data.objects.new("Point",  point_light_data)
point_light.location = (0.0071, 0.1756, 0.4689)
point_light.data.energy = 2.4 # keep this below 15
point_light.data.color = (0.8, 1.0, 0.85)
point_light.data.shadow_soft_size = 0.0
bpy.context.collection.objects.link(point_light)


# --- materials code ---

for mat in bpy.data.materials:
    if mat.use_nodes:
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        principled = None
        output = None
        emission_node = None

        for node in nodes:
            if node.type == 'BSDF_PRINCIPLED':
                principled = node
            elif node.type == 'OUTPUT_MATERIAL':
                output = node
            elif node.type == 'EMISSION':
                emission_node = node

        # Make the material neon green, glossy, and emissive
        if principled:
            if 'Base Color' in principled.inputs:
                principled.inputs['Base Color'].default_value = (0.05, 1.0, 0.12, 1.0)
            if 'Roughness' in principled.inputs:
                principled.inputs['Roughness'].default_value = 0.12
            if 'Metallic' in principled.inputs:
                principled.inputs['Metallic'].default_value = 0.15
            if 'Emission' in principled.inputs:
                principled.inputs['Emission'].default_value = (0.05, 1.0, 0.12, 1.0)
            if 'Emission Strength' in principled.inputs:
                principled.inputs['Emission Strength'].default_value = 12.0

        # If an Emission node exists, ensure it is connected to the output for a stronger glow-like look
        if emission_node and output:
            # Clear existing surface links to avoid conflicts
            for link in list(output.inputs['Surface'].links):
                links.remove(link)
            if 'Color' in emission_node.inputs:
                emission_node.inputs['Color'].default_value = (0.05, 1.0, 0.12, 1.0)
            if 'Strength' in emission_node.inputs:
                emission_node.inputs['Strength'].default_value = 20.0
            links.new(emission_node.outputs['Emission'], output.inputs['Surface'])


# --- lighting code ---

# Rebalance toward intense green illumination with stronger contrast
# Reduce environment contribution so the colored lights read more strongly.
bpy.data.worlds["World.001"].node_tree.nodes["HDRIHandler_ShaderNodeBackground"].inputs[1].default_value = 0.75

# Push the main key light into a vivid green tone and keep it strong for highlights.
area_light.data.color = (0.95, 1.0, 0.95) # (R, G, B )
area_light.data.energy = 12.73 # keep this below 15.

# Make the back fill greener but softer to avoid flattening contrast.
area_light001.data.color = (0.95, 1.0, 0.95) # (R, G, B )
area_light001.data.energy = 12.73 # keep this below 15

# Remove pink influence from the left light and convert it to a subtle green accent.
area_light002.data.color = (0.35, 1.0, 0.45) # neon-green tint
area_light002.data.energy = 1.27 # keep this below 15

# Keep top light neutral but lower it so it doesn't compete with the green key.
area_light003.data.color = (0.95, 1.0, 0.95) # (R, G, B )
area_light003.data.energy = 8.91  # keep this below 15

# Reduce the point light so it doesn't add unwanted warm/neutral fill.
point_light.data.color = (0.8, 1.0, 0.85)
point_light.data.energy = 2.4 # keep this below 15

# Optional: slightly sharpen perceived contrast by reducing light softness where possible.
area_light.data.shadow_soft_size = 3.14
area_light001.data.shadow_soft_size = 3.14
area_light002.data.shadow_soft_size = 3.14
area_light003.data.shadow_soft_size = 3.14
point_light.data.shadow_soft_size = 0.0

# --- background code ---


# --- Background tuning: darker, more muted support for the neon-green object ---
world = bpy.data.worlds.get("World.001")
if world and world.use_nodes and world.node_tree:
    nodes = world.node_tree.nodes
    bg_node = nodes.get("HDRIHandler_ShaderNodeBackground")
    if bg_node is None:
        # Fallback: find any Background node in the world tree
        for n in nodes:
            if n.type == 'BACKGROUND':
                bg_node = n
                break
    if bg_node:
        # Dark muted gray-blue background
        bg_node.inputs[0].default_value = (0.05, 0.06, 0.07, 1.0)
        # Slightly reduced brightness for a subtler background
        bg_node.inputs[1].default_value = 0.25
