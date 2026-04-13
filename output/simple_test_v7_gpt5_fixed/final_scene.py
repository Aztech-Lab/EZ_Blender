import bpy

# setting the strength of the HDR to be 0.9, which is strong. Decrease if you want less environment light coming in.
# for darker scenes, set this to 0.05. (like night scenes, with scenes with darker backgrounds)
# do not exceed 1.0 for this value.
bpy.data.worlds["World.001"].node_tree.nodes["HDRIHandler_ShaderNodeBackground"].inputs[1].default_value = 0.18
# NOTE: for darker scenes, make sure that the energy values below of each light is also low -- otherwise everything
# will be too bright.

# Area light 1: light from the right hand side
area_light_data = bpy.data.lights.new('light', type="AREA")
area_light = bpy.data.objects.new("Area",  area_light_data)
area_light.location = (0.7558, -0.2978, 0.2950 ) # (x,y, z)
area_light.scale = (0.4320, 0.1758, 0.4320) # (scale_x, scale_y, scale_z)
area_light.rotation_euler = (0.7196, 1.5708, 0) # (radians_x, radians_y, radians_z)
area_light.data.energy = 4.0
area_light.data.color = (1,1,1) # (R, G, B )
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
area_light001.data.energy = 3.5
area_light001.data.color = (1.0, 1.0, 1.0) # (R, G, B )
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
area_light002.data.energy = 0.4
area_light002.data.color = (1.0, 0.6631, 0.7528) # (R, G, B )
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
area_light003.data.energy = 12.0
area_light003.data.color = (1.0, 1.0, 1.0) # (R, G, B )
area_light003.data.shape = "SQUARE"
area_light003.data.size = 1.0
area_light003.data.shadow_soft_size = 3.14
bpy.context.collection.objects.link(area_light003)

# Point light 1: Slightly behind the lotion.
point_light_data = bpy.data.lights.new('light', type="POINT")
point_light = bpy.data.objects.new("Point",  point_light_data)
point_light.location = (0.0071, 0.1756, 0.4689)
point_light.data.energy = 0.2
point_light.data.color = (1.0, 1.0, 1.0)
point_light.data.shadow_soft_size = 0.0
bpy.context.collection.objects.link(point_light)


# --- materials code ---

for mat in bpy.data.materials:
    if mat.use_nodes:
        # Get the Principled BSDF or add an Emission shader
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Remove existing links to Material Output
        output_node = None
        for node in nodes:
            if node.type == 'OUTPUT_MATERIAL':
                output_node = node
                break
        if output_node is None:
            output_node = nodes.new(type='ShaderNodeOutputMaterial')
            output_node.location = (300, 0)

        # Clear existing shader links into Surface
        for link in list(links):
            if link.to_node == output_node and link.to_socket.name == 'Surface':
                links.remove(link)

        # Remove Principled BSDF if present
        principled = None
        for node in nodes:
            if node.type == 'BSDF_PRINCIPLED':
                principled = node
                break
        if principled is not None:
            nodes.remove(principled)

        # Remove any existing Emission node to avoid duplicates
        for node in list(nodes):
            if node.type == 'EMISSION':
                nodes.remove(node)

        emission = nodes.new(type='ShaderNodeEmission')
        emission.location = (0, 0)
        emission.inputs['Color'].default_value = (1.0, 0.0, 0.0, 1.0)
        emission.inputs['Strength'].default_value = 25.0

        links.new(emission.outputs['Emission'], output_node.inputs['Surface'])

        # Make the material as non-reflective as possible
        if hasattr(mat, 'blend_method'):
            mat.blend_method = 'OPAQUE'
        if hasattr(mat, 'shadow_method'):
            mat.shadow_method = 'NONE'
        if hasattr(mat, 'use_backface_culling'):
            mat.use_backface_culling = False


# --- lighting code ---

# --- Low-key neon-focused lighting adjustments ---
# Reduce environment contribution so emission dominates.
bpy.data.worlds["World.001"].node_tree.nodes["HDRIHandler_ShaderNodeBackground"].inputs[1].default_value = 0.18

# Dim the existing studio lights substantially.
for light_name in ["Area", "Area.001", "Area.002", "Area.003", "Point"]:
    obj = bpy.data.objects.get(light_name)
    if obj and obj.type == 'LIGHT':
        obj.data.energy *= 0.18

# Add a subtle cool rim light to outline the subject without flattening the neon glow.
rim_data = bpy.data.lights.new('NeonRim', type='AREA')
rim = bpy.data.objects.new('NeonRim', rim_data)
rim.location = (0.62, -0.58, 0.42)
rim.rotation_euler = (1.35, 0.15, 0.95)
rim.scale = (0.55, 0.18, 0.55)
rim.data.shape = 'RECTANGLE'
rim.data.size = 1.0
rim.data.size_y = 0.35
rim.data.energy = 1.1
rim.data.color = (0.55, 0.75, 1.0)
rim.data.shadow_soft_size = 3.0
bpy.context.collection.objects.link(rim)

# Add a very faint warm fill from the front to retain minimal form in shadows.
fill_data = bpy.data.lights.new('NeonFill', type='AREA')
fill = bpy.data.objects.new('NeonFill', fill_data)
fill.location = (-0.15, -0.22, 0.28)
fill.rotation_euler = (1.65, 0.0, 0.0)
fill.scale = (0.35, 0.35, 0.35)
fill.data.shape = 'SQUARE'
fill.data.size = 0.8
fill.data.energy = 0.35
fill.data.color = (1.0, 0.72, 0.78)
fill.data.shadow_soft_size = 4.0
bpy.context.collection.objects.link(fill)

# Optional: slightly darken world background color if present, to keep the scene moody.
world = bpy.data.worlds.get("World.001")
if world and world.node_tree:
    bg = world.node_tree.nodes.get("HDRIHandler_ShaderNodeBackground")
    if bg:
        bg.inputs[0].default_value = (0.02, 0.02, 0.025, 1.0)

# --- background code ---

# Darken and simplify the world backdrop for stronger neon/red contrast
world = bpy.data.worlds.get("World.001")
if world is not None:
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes.get("HDRIHandler_ShaderNodeBackground")
    if bg is not None:
        # Lower environment brightness
        bg.inputs[1].default_value = 0.15
        # Set a darker, neutral backdrop color
        bg.inputs[0].default_value = (0.02, 0.02, 0.025, 1.0)

    # Optional: also reduce ambient world contribution if present
    for node in nt.nodes:
        if node.type == 'BACKGROUND':
            node.inputs[1].default_value = min(node.inputs[1].default_value, 0.15)
            node.inputs[0].default_value = (0.02, 0.02, 0.025, 1.0)
