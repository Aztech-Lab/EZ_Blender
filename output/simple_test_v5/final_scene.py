import bpy

# setting the strength of the HDR to be 0.9, which is strong. Decrease if you want less environment light coming in.
# for darker scenes, set this to 0.05. (like night scenes, with scenes with darker backgrounds)
# do not exceed 1.0 for this value.
bpy.data.worlds["World.001"].node_tree.nodes["HDRIHandler_ShaderNodeBackground"].inputs[1].default_value = 0.9
# NOTE: for darker scenes, make sure that the energy values below of each light is also low -- otherwise everything
# will be too bright.

# Area light 1: light from the right hand side
area_light_data = bpy.data.lights.new('light', type='AREA')
area_light = bpy.data.objects.new('Area', area_light_data)
area_light.location = (0.7558, -0.2978, 0.2950)
area_light.scale = (0.4320, 0.1758, 0.4320)
area_light.rotation_euler = (0.7196, 1.5708, 0)
area_light.data.energy = 12.73
area_light.data.color = (1, 1, 1)
area_light.data.shape = 'SQUARE'
area_light.data.size = 1.0
area_light.data.shadow_soft_size = 3.14
bpy.context.collection.objects.link(area_light)

# Area light 2: Light reflecting off the back wall
area_light001_data = bpy.data.lights.new('light', type='AREA')
area_light001 = bpy.data.objects.new('Area.001', area_light001_data)
area_light001.location = (-0.4267, 0.3767, 0.4435)
area_light001.scale = (0.6872, 0.6872, 0.6872)
area_light001.rotation_euler = (1.1453, -0.0616, -0.0223)
area_light001.data.energy = 12.73
area_light001.data.color = (1.0, 1.0, 1.0)
area_light001.data.shape = 'SQUARE'
area_light001.data.size = 1.0
area_light001.data.shadow_soft_size = 3.14
bpy.context.collection.objects.link(area_light001)

# Area light 3: Light on the left hand side
area_light002_data = bpy.data.lights.new('light', type='AREA')
area_light002 = bpy.data.objects.new('Area.002', area_light002_data)
area_light002.location = (-0.3151, -0.4322, 0.3610)
area_light002.scale = (1.0, 1.0, 1.0)
area_light002.rotation_euler = (1.2139, 0.0966, -0.6434)
area_light002.data.energy = 1.27
area_light002.data.color = (1.0, 0.6631, 0.7528)
area_light002.data.shape = 'SQUARE'
area_light002.data.size = 0.46
area_light002.data.shadow_soft_size = 3.14
bpy.context.collection.objects.link(area_light002)

# Area light 4: Light coming straight down from the top
area_light003_data = bpy.data.lights.new('light', type='AREA')
area_light003 = bpy.data.objects.new('Area.003', area_light003_data)
area_light003.location = (0.0000, 0.0000, 1.1032)
area_light003.scale = (1.0, 1.0, 1.0)
area_light003.rotation_euler = (0, 0, 0)
area_light003.data.energy = 8.91
area_light003.data.color = (1.0, 1.0, 1.0)
area_light003.data.shape = 'SQUARE'
area_light003.data.size = 1.0
area_light003.data.shadow_soft_size = 3.14
bpy.context.collection.objects.link(area_light003)

# Point light 1: Slightly behind the lotion.
point_light_data = bpy.data.lights.new('light', type='POINT')
point_light = bpy.data.objects.new('Point', point_light_data)
point_light.location = (0.0071, 0.1756, 0.4689)
point_light.data.energy = 2.4
point_light.data.color = (1.0, 1.0, 1.0)
point_light.data.shadow_soft_size = 0.0
bpy.context.collection.objects.link(point_light)


# --- materials fixed code ---

for mat in bpy.data.materials:
    if mat.use_nodes:
        # Get the node tree
        nodes = material.node_tree.nodes
        # Clear existing nodes
        nodes.clear()
        # Add Emission Shader
        emission_node = nodes.new(type='ShaderNodeEmission')
        emission_node.inputs[0].default_value = (1.0, 0.0, 0.0, 1.0)  # Red color with full alpha
        emission_node.inputs[1].default_value = 5.0  # Strength of the emission
        # Add Material Output
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        # Link Emission to Output
        mat.node_tree.links.new(emission_node.outputs[0], output_node.inputs[0])

# --- lighting fixed code ---

import bpy

# Reduce the energy of existing lights to focus on the neon glow
bpy.data.objects['Area'].data.energy = 6.0
bpy.data.objects['Area.001'].data.energy = 6.0
bpy.data.objects['Area.002'].data.energy = 0.5
bpy.data.objects['Area.003'].data.energy = 4.0
bpy.data.objects['Point'].data.energy = 1.2

# Add a new point light to enhance the neon glow effect
neon_glow_light_data = bpy.data.lights.new('neon_glow', type='POINT')
neon_glow_light = bpy.data.objects.new('NeonGlow', neon_glow_light_data)
neon_glow_light.location = (0.0, 0.0, 0.5)  # Position near the glowing object
neon_glow_light.data.energy = 10.0  # High energy for strong glow
neon_glow_light.data.color = (1.0, 0.0, 0.0)  # Red color for neon effect
neon_glow_light.data.shadow_soft_size = 0.1
bpy.context.collection.objects.link(neon_glow_light)

# --- background fixed code ---


# Adjust the world background color to complement the neon red glow
world = bpy.data.worlds['World.001']
world.use_nodes = True

# Access the background node
bg_node = world.node_tree.nodes['Background']

# Set a subtle complementary background color
# A darker, desaturated color will help the neon red stand out
bg_node.inputs[0].default_value = (0.1, 0.1, 0.1, 1)  # RGBA format

# Reduce the background strength to avoid overpowering the neon glow
bg_node.inputs[1].default_value = 0.5  # Lowering from 0.9 to 0.5
