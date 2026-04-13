import bpy

# setting the strength of the HDR to be 0.9, which is strong. Decrease if you want less environment light coming in.
# for darker scenes, set this to 0.05. (like night scenes, with scenes with darker backgrounds)
# do not exceed 1.0 for this value.
bpy.data.worlds["World.001"].node_tree.nodes["HDRIHandler_ShaderNodeBackground"].inputs[1].default_value = 0.9
# NOTE: for darker scenes, make sure that the energy values below of each light is also low -- otherwise everything
# will be too bright.

# Area light 1: light from the right hand side
area_light_data = bpy.data.lights.new('light', type="AREA")
area_light = bpy.data.objects.new("Area",  area_light_data)
area_light.location =  (0.7558, -0.2978, 0.2950 ) # (x,y, z)
area_light.scale = (0.4320, 0.1758, 0.4320) # (scale_x, scale_y, scale_z)
area_light.rotation_euler = (0.7196, 1.5708, 0) # (radians_x, radians_y, radians_z)
area_light.data.energy = 12.73 # keep this below 15.
area_light.data.color = (1,1,1) # (R, G, B )
area_light.data.shape = "SQUARE"
area_light.data.size = 1.0
area_light.data.shadow_soft_size = 3.14
bpy.context.collection.objects.link(area_light)

# Area light 2: Light reflecting off the back wall
area_light001_data =  bpy.data.lights.new('light', type="AREA")
area_light001 = bpy.data.objects.new("Area.001",  area_light001_data)
area_light001.location = (-0.4267, 0.3767, 0.4435) # (x,y, z)
area_light001.scale = (0.6872, 0.6872, 0.6872) # (scale_x, scale_y, scale_z)
area_light001.rotation_euler = (1.1453, -0.0616, -0.0223) # (radians_x, radians_y, radians_z)
area_light001.data.energy = 12.73 # keep this below 15
area_light001.data.color = (1.0, 1.0, 1.0) # (R, G, B )
area_light001.data.shape = "SQUARE"
area_light001.data.size = 1.0
area_light001.data.shadow_soft_size = 3.14
bpy.context.collection.objects.link(area_light001)

# Area light 3: Light on the left hand side
area_light002_data =  bpy.data.lights.new('light', type="AREA")
area_light002 = bpy.data.objects.new("Area.002",  area_light002_data)
area_light002.location = (-0.3151, -0.4322, 0.3610) # (x,y, z)
area_light002.scale = (1.0, 1.0 , 1.0 ) # (scale_x, scale_y, scale_z)
area_light002.rotation_euler = (1.2139, 0.0966, -0.6434)  # (radians_x, radians_y, radians_z)
area_light002.data.energy = 1.27 # keep this below 15
area_light002.data.color =  (1.0, 0.6631, 0.7528) # (R, G, B )
area_light002.data.shape = "SQUARE"
area_light002.data.size = 0.46
area_light002.data.shadow_soft_size = 3.14
bpy.context.collection.objects.link(area_light002)

# Area light 4: Light coming straight down from the top
area_light003_data =  bpy.data.lights.new('light', type="AREA")
area_light003 = bpy.data.objects.new("Area.003",  area_light003_data)
area_light003.location =  (0.0000, 0.0000, 1.1032) # (x,y, z)
area_light003.scale = (1.0, 1.0 , 1.0 ) # (scale_x, scale_y, scale_z)
area_light003.rotation_euler = (0, 0, 0)  # (radians_x, radians_y, radians_z)
area_light003.data.energy = 8.91  # keep this below 15
area_light003.data.color =  (1.0, 1.0, 1.0) # (R, G, B )
area_light003.data.shape = "SQUARE"
area_light003.data.size = 1.0
area_light003.data.shadow_soft_size = 3.14
bpy.context.collection.objects.link(area_light003)

# Point light 1: Slightly behind the lotion.
point_light_data =  bpy.data.lights.new('light', type="POINT")
point_light = bpy.data.objects.new("Point",  point_light_data)
point_light.location = (0.0071, 0.1756, 0.4689) 
point_light.data.energy = 2.4 # keep this below 15
point_light.data.color = (1.0, 1.0, 1.0)
point_light.data.shadow_soft_size = 0.0
bpy.context.collection.objects.link(point_light)


# --- materials code ---

for mat in bpy.data.materials:
    if mat.use_nodes:
        nodes = neon_red_material.node_tree.nodes
        links = neon_red_material.node_tree.links
        
        # Add an Emission shader node
        emission_node = nodes.new(type='ShaderNodeEmission')
        emission_node.inputs['Strength'].default_value = 10.0  # Increase strength for neon effect
        
        # Connect Emission shader to Material Output
        material_output = nodes.get('Material Output')
        links.new(emission_node.outputs['Emission'], material_output.inputs['Surface'])

# --- lighting code ---



# Adding a neon emission plane to enhance the glow effect
neon_material = bpy.data.materials.new(name="NeonMaterial")
neon_material.use_nodes = True
bsdf = neon_material.node_tree.nodes.get('Principled BSDF')
if bsdf:
    neon_material.node_tree.nodes.remove(bsdf)
emission = neon_material.node_tree.nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value = (0.0, 1.0, 0.0, 1)  # Bright green color
emission.inputs['Strength'].default_value = 50.0  # High emission strength for a strong glow
output = neon_material.node_tree.nodes.get('Material Output')
neon_material.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])

# Create the emission plane
neon_plane = bpy.data.objects.new("NeonPlane", bpy.data.meshes.new("NeonPlaneMesh"))
bpy.context.collection.objects.link(neon_plane)

# Set the location and scale of the neon plane
neon_plane.location = (0.0, 0.0, 0.5)  # Adjust as needed for the scene
neon_plane.scale = (0.5, 0.5, 0.01)

# Assign the neon material to the plane
neon_plane.data.materials.append(neon_material)

# Reduce the energy of existing lights to enhance the glow effect
area_light.data.energy = 6.0
area_light001.data.energy = 6.0
area_light002.data.energy = 0.6
area_light003.data.energy = 4.5
point_light.data.energy = 1.2

# Adjust HDR strength for a balanced environment light
bpy.data.worlds["World.001"].node_tree.nodes["HDRIHandler_ShaderNodeBackground"].inputs[1].default_value = 0.3

# --- background code ---



# Change world background color to a darker shade or complementary color
bpy.data.worlds['World.001'].node_tree.nodes['Background'].inputs[0].default_value = (0.1, 0.1, 0.1, 1)  # Dark gray color

# Reduce world background brightness
bpy.data.worlds['World.001'].node_tree.nodes['Background'].inputs[1].default_value = 0.5  # Reduce brightness to half
