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
area_light.location = (0.7558, -0.2978, 0.2950 ) # (x,y, z)
area_light.scale = (0.4320, 0.1758, 0.4320) # (scale_x, scale_y, scale_z)
area_light.rotation_euler = (0.7196, 1.5708, 0) # (radians_x, radians_y, radians_z)
area_light.data.energy = 12.73 # keep this below 15.
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
area_light001.data.energy = 12.73 # keep this below 15
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
area_light002.data.energy = 1.27 # keep this below 15
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
area_light003.data.energy = 8.91  # keep this below 15
area_light003.data.color = (1.0, 1.0, 1.0) # (R, G, B )
area_light003.data.shape = "SQUARE"
area_light003.data.size = 1.0
area_light003.data.shadow_soft_size = 3.14
bpy.context.collection.objects.link(area_light003)

# Point light 1: Slightly behind the lotion.
point_light_data = bpy.data.lights.new('light', type="POINT")
point_light = bpy.data.objects.new("Point",  point_light_data)
point_light.location = (0.0071, 0.1756, 0.4689)
point_light.data.energy = 2.4 # keep this below 15
point_light.data.color = (1.0, 1.0, 1.0)
point_light.data.shadow_soft_size = 0.0
bpy.context.collection.objects.link(point_light)


# --- materials code ---

for mat in bpy.data.materials:
    if mat.use_nodes:
        nodes = mat.node_tree.nodes
        for node in nodes:
            if node.type == 'BSDF_PRINCIPLED':
                # Set the base color to a neon-like color
                node.inputs['Base Color'].default_value = (0.0, 1.0, 0.0, 1.0)  # Neon green
                # Increase emission to create a glow effect
                emission_node = nodes.new(type='ShaderNodeEmission')
                emission_node.inputs['Color'].default_value = (0.0, 1.0, 0.0, 1.0)  # Neon green
                emission_node.inputs['Strength'].default_value = 10.0
                # Increase metallic for reflective sheen
                node.inputs['Metallic'].default_value = 0.8
                # Slightly reduce roughness for shininess
                node.inputs['Roughness'].default_value = 0.1
                # Link emission to material output
                material_output = nodes.get('Material Output')
                mat.node_tree.links.new(emission_node.outputs['Emission'], material_output.inputs['Surface'])

# --- lighting code ---



# Blue neon light replacing Area light 1
area_light.data.color = (1,1,1) # (R, G, B )
area_light.data.energy = 12.73 # keep this below 15.

# Blue neon light replacing Area light 2
area_light001.data.color = (1.0, 1.0, 1.0) # (R, G, B )
area_light001.data.energy = 12.73 # keep this below 15

# Pink accent replacing Area light 3
area_light002.data.color = (1.0, 0.6631, 0.7528) # (R, G, B )
area_light002.data.energy = 1.27 # keep this below 15

# Purple accent from Area light 4
area_light003.data.color = (1.0, 1.0, 1.0) # (R, G, B )
area_light003.data.energy = 8.91  # keep this below 15

# Additional blue point light for neon effect
neon_point_light_data = bpy.data.lights.new('neon_light', type="POINT")
neon_point_light = bpy.data.objects.new("Neon_Point", neon_point_light_data)
neon_point_light.location = (0.0, 0.0, 1.0)  # Position above the scene
neon_point_light.data.energy = 25.0  # High energy for neon effect
neon_point_light.data.color = (0.0, 0.0, 1.0)  # Blue color
bpy.context.collection.objects.link(neon_point_light)

# Adjust HDRI strength for a darker nightclub ambiance
bpy.data.worlds["World.001"].node_tree.nodes["HDRIHandler_ShaderNodeBackground"].inputs[1].default_value = 0.9

# --- camera code ---

import bpy

# Create a new camera
camera_data = bpy.data.cameras.new(name='CustomCamera')
camera_object = bpy.data.objects.new('CustomCamera', camera_data)
bpy.context.scene.collection.objects.link(camera_object)

# Position the camera at a lower angle
camera_object.location = (0, -5, 1)  # Lower position looking up

# Rotate the camera to face upwards
camera_object.rotation_euler = (1.3, 0, 0)  # Tilted upwards

# Set the camera as the active scene camera
bpy.context.scene.camera = camera_object


# --- background code ---


# Change the world background color to a darker shade with blues and purples.
world = bpy.data.worlds['World.001']
world.use_nodes = True

# Access the node tree
node_tree = world.node_tree

# Remove existing nodes
for node in node_tree.nodes:
    node_tree.nodes.remove(node)

# Add Background node
bg_node = node_tree.nodes.new(type='ShaderNodeBackground')

# Add Color Ramp for gradient effect
color_ramp = node_tree.nodes.new(type='ShaderNodeValToRGB')
color_ramp.color_ramp.elements[0].position = 0.3
color_ramp.color_ramp.elements[0].color = (0.1, 0.1, 0.3, 1)  # Dark blue
color_ramp.color_ramp.elements[1].position = 0.7
color_ramp.color_ramp.elements[1].color = (0.3, 0.0, 0.3, 1)  # Dark purple

# Add Texture Coordinate and Mapping nodes for control
tex_coord = node_tree.nodes.new(type='ShaderNodeTexCoord')
mapping = node_tree.nodes.new(type='ShaderNodeMapping')

# Add links between nodes
node_tree.links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
node_tree.links.new(mapping.outputs['Vector'], color_ramp.inputs['Fac'])
node_tree.links.new(color_ramp.outputs['Color'], bg_node.inputs['Color'])

# Add Output node
output_node = node_tree.nodes.new(type='ShaderNodeOutputWorld')
node_tree.links.new(bg_node.outputs['Background'], output_node.inputs['Surface'])

# Adjust the strength of the background
bg_node.inputs[1].default_value = 0.5  # Adjust brightness as needed