import bpy

# setting the strength of the HDR to be 0.9, which is strong. Decrease if you want less environment light coming in.
# for darker scenes, set this to 0.05. (like night scenes, with scenes with darker backgrounds)
# do not exceed 1.0 for this value.
bpy.data.worlds["World.001"].node_tree.nodes["HDRIHandler_ShaderNodeBackground"].inputs[1].default_value = 0.65
# NOTE: for darker scenes, make sure that the energy values below of each light is also low -- otherwise everything
# will be too bright.

# Area light 1: light from the right hand side
area_light_data = bpy.data.lights.new('light', type="AREA")
area_light = bpy.data.objects.new("Area",  area_light_data)
area_light.location = (0.7558, -0.2978, 0.2950 ) # (x,y, z)
area_light.scale = (0.4320, 0.1758, 0.4320) # (scale_x, scale_y, scale_z)
area_light.rotation_euler = (0.7196, 1.5708, 0) # (radians_x, radians_y, radians_z)
area_light.data.energy = 14.5 # keep this below 15.
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
area_light001.data.energy = 10.5 # keep this below 15
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
area_light002.data.energy = 1.0 # keep this below 15
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
area_light003.data.energy = 7.5  # keep this below 15
area_light003.data.color = (1.0, 1.0, 1.0) # (R, G, B )
area_light003.data.shape = "SQUARE"
area_light003.data.size = 1.0
area_light003.data.shadow_soft_size = 3.14
bpy.context.collection.objects.link(area_light003)

# Point light 1: Slightly behind the lotion.
point_light_data = bpy.data.lights.new('light', type="POINT")
point_light = bpy.data.objects.new("Point",  point_light_data)
point_light.location = (0.0071, 0.1756, 0.4689)
point_light.data.energy = 1.8 # keep this below 15
point_light.data.color = (1.0, 1.0, 1.0)
point_light.data.shadow_soft_size = 0.0
bpy.context.collection.objects.link(point_light)


# --- materials code ---

for mat in bpy.data.materials:
    if mat.use_nodes:
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Find Principled BSDF and make the surface more reflective/glossy
        for node in nodes:
            if node.type == 'BSDF_PRINCIPLED':
                # Brighter specular edges
                if 'Specular' in node.inputs:
                    node.inputs['Specular'].default_value = 0.65
                if 'Specular IOR Level' in node.inputs:
                    node.inputs['Specular IOR Level'].default_value = 0.65
                
                # More pronounced glossy highlights
                if 'Roughness' in node.inputs:
                    node.inputs['Roughness'].default_value = 0.18
                
                # Add a subtle clearcoat for sharper rim reflections
                if 'Clearcoat' in node.inputs:
                    node.inputs['Clearcoat'].default_value = 0.35
                if 'Clearcoat Roughness' in node.inputs:
                    node.inputs['Clearcoat Roughness'].default_value = 0.08
                
                # Slight sheen can help catch colored grazing light on curved surfaces
                if 'Sheen' in node.inputs:
                    node.inputs['Sheen'].default_value = 0.12
                if 'Sheen Roughness' in node.inputs:
                    node.inputs['Sheen Roughness'].default_value = 0.35
                
                # Keep base color unchanged; only enhance reflectivity response
                break

# --- lighting code ---

# Reduce ambient HDRI contribution for a darker, more contrasty neon look
bpy.data.worlds["World.001"].node_tree.nodes["HDRIHandler_ShaderNodeBackground"].inputs[1].default_value = 0.65

# Make the main right-side light a cool blue rim light
area_light.data.energy = 14.5 # keep this below 15.
area_light.data.color = (1,1,1) # (R, G, B )
area_light.location = (0.7558, -0.2978, 0.2950 ) # (x,y, z)
area_light.rotation_euler = (0.7196, 1.5708, 0) # (radians_x, radians_y, radians_z)

# Turn the back wall light into a strong pink/magenta accent
area_light001.data.energy = 10.5 # keep this below 15
area_light001.data.color = (1.0, 1.0, 1.0) # (R, G, B )
area_light001.location = (-0.4267, 0.3767, 0.4435) # (x,y, z)
area_light001.rotation_euler = (1.1453, -0.0616, -0.0223) # (radians_x, radians_y, radians_z)

# Dim the left light so it only provides a subtle complementary pink edge
area_light002.data.energy = 1.0 # keep this below 15
area_light002.data.color = (1.0, 0.6631, 0.7528) # (R, G, B )
area_light002.location = (-0.3151, -0.4322, 0.3610) # (x,y, z)

# Reduce top fill to preserve deep shadows
area_light003.data.energy = 7.5  # keep this below 15
area_light003.data.color = (1.0, 1.0, 1.0) # (R, G, B )
area_light003.location = (0.0000, 0.0000, 1.1032) # (x,y, z)

# Keep the point light very subtle so it doesn't flatten the contrast
point_light.data.energy = 1.8 # keep this below 15
point_light.data.color = (1.0, 1.0, 1.0)


# --- background code ---

# --- Cyberpunk background adjustment: darker, cooler world lighting ---
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
        # Dark blue-purple background to support neon pink/blue accents
        bg_node.inputs[0].default_value = (0.03, 0.04, 0.08, 1.0)  # Color
        bg_node.inputs[1].default_value = 0.12  # Strength

    # Optional: slightly cooler world ambient tint if a color socket exists elsewhere
    # Keep the environment subdued so the product remains the focus.
