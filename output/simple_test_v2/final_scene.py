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
        nodes = material.node_tree.nodes
        # Check if there's an Emission shader node
        emission_node = nodes.get('Emission')
        if not emission_node:
            # Create an Emission shader node if it doesn't exist
            emission_node = nodes.new(type='ShaderNodeEmission')
        # Set the emission color and strength
        emission_node.inputs['Color'].default_value = (1.0, 0.5, 0.0, 1.0)  # Orange glow
        emission_node.inputs['Strength'].default_value = 5.0
        # Link the emission node to the material output
        material_output = nodes.get('Material Output')
        if material_output:
            mat.node_tree.links.new(emission_node.outputs['Emission'], material_output.inputs['Surface'])

# --- lighting code ---

import bpy

# Emission shader for neon glow effect
neon_mat = bpy.data.materials.new(name="NeonMaterial")
neon_mat.use_nodes = True
emission_node = neon_mat.node_tree.nodes.new(type='ShaderNodeEmission')
emission_node.inputs['Color'].default_value = (0.0, 1.0, 0.8, 1)  # Cyan glow
emission_node.inputs['Strength'].default_value = 10.0  # Intensity of the glow

output_node = neon_mat.node_tree.nodes['Material Output']
neon_mat.node_tree.links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])

# Create a neon tube to apply the emission shader
bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=2.0, location=(0, 0, 0.5))
neon_tube = bpy.context.object
neon_tube.data.materials.append(neon_mat)

# Add a point light to enhance the neon glow
neon_glow_light_data = bpy.data.lights.new(name="NeonGlowLight", type='POINT')
neon_glow_light = bpy.data.objects.new(name="NeonGlowLight", object_data=neon_glow_light_data)
neon_glow_light.location = (0, 0, 0.5)
neon_glow_light.data.energy = 5.0  # Moderate energy to enhance glow
neon_glow_light.data.color = (0.0, 1.0, 0.8)  # Same color as neon emission
bpy.context.collection.objects.link(neon_glow_light)

# Adjust existing area lights to complement neon theme
bpy.data.objects['Area'].data.color = (0.5, 0.5, 0.5)  # Neutral color
bpy.data.objects['Area.001'].data.color = (0.5, 0.5, 0.5)  # Neutral color
bpy.data.objects['Area.002'].data.color = (0.5, 0.5, 0.5)  # Neutral color
bpy.data.objects['Area.003'].data.color = (0.5, 0.5, 0.5)  # Neutral color

# Reduce the energy of existing lights
bpy.data.objects['Area'].data.energy = 6.0
bpy.data.objects['Area.001'].data.energy = 6.0
bpy.data.objects['Area.002'].data.energy = 1.0
bpy.data.objects['Area.003'].data.energy = 4.0
bpy.data.objects['Point'].data.energy = 1.2

# --- background code ---



# Change the world background color to complement neon red
world = bpy.data.worlds['World.001']
world.use_nodes = True
bg_node = world.node_tree.nodes['Background']

# Set the world color to a dark, neutral tone
bg_node.inputs[0].default_value = (0.1, 0.1, 0.1, 1)  # Dark grey color

# Adjust the brightness of the world background
bg_node.inputs[1].default_value = 0.5  # Dim the background to make neon colors pop
