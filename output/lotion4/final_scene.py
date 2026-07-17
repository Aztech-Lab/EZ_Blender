import bpy

# setting the strength of the HDR to be 0.9, which is strong. Decrease if you want less environment light coming in.
# for darker scenes, set this to 0.05. (like night scenes, with scenes with darker backgrounds)
# do not exceed 1.0 for this value.
bpy.data.worlds["World.001"].node_tree.nodes["HDRIHandler_ShaderNodeBackground"].inputs[1].default_value = 0.35
# NOTE: for darker scenes, make sure that the energy values below of each light is also low -- otherwise everything
# will be too bright.

# Area light 1: light from the right hand side
area_light_data = bpy.data.lights.new('light', type="AREA")
area_light = bpy.data.objects.new("Area",  area_light_data)
area_light.location =  (0.7558, -0.2978, 0.2950 ) # (x,y, z)
area_light.scale = (0.4320, 0.1758, 0.4320) # (scale_x, scale_y, scale_z)
area_light.rotation_euler = (0.7196, 1.5708, 0) # (radians_x, radians_y, radians_z)
area_light.data.energy = 14.5
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
area_light001.data.energy = 10.8
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
area_light002.data.energy = 3.2
area_light002.data.color = (0.75, 0.85, 1.0)
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
area_light003.data.energy = 5.6
area_light003.data.color =  (1.0, 1.0, 1.0) # (R, G, B )
area_light003.data.shape = "SQUARE"
area_light003.data.size = 1.0
area_light003.data.shadow_soft_size = 3.14
bpy.context.collection.objects.link(area_light003)

# Point light 1: Slightly behind the lotion.
point_light_data =  bpy.data.lights.new('light', type="POINT")
point_light = bpy.data.objects.new("Point",  point_light_data)
point_light.location = (0.0071, 0.1756, 0.4689) 
point_light.data.energy = 4.0
point_light.data.color = (1.0, 1.0, 1.0)
point_light.data.shadow_soft_size = 0.0
bpy.context.collection.objects.link(point_light)


# --- materials code ---

for mat in bpy.data.materials:
    if mat.use_nodes:
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Target bottle/cap materials by name when possible
        name_l = mat.name.lower()
        if any(k in name_l for k in ["bottle", "cap", "lid", "top"]):
            for node in nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    # Reflective tech-style surface
                    if 'Base Color' in node.inputs:
                        node.inputs['Base Color'].default_value = (0.08, 0.12, 0.18, 1.0)
                    if 'Metallic' in node.inputs:
                        node.inputs['Metallic'].default_value = 0.85
                    if 'Roughness' in node.inputs:
                        node.inputs['Roughness'].default_value = 0.18
                    if 'Specular' in node.inputs:
                        node.inputs['Specular'].default_value = 0.65
                    if 'Clearcoat' in node.inputs:
                        node.inputs['Clearcoat'].default_value = 0.7
                    if 'Clearcoat Roughness' in node.inputs:
                        node.inputs['Clearcoat Roughness'].default_value = 0.03
                    
                    # Subtle iridescent/neon accent via emission
                    if 'Emission' in node.inputs:
                        node.inputs['Emission'].default_value = (0.0, 0.9, 1.0, 1.0)
                    if 'Emission Strength' in node.inputs:
                        node.inputs['Emission Strength'].default_value = 0.8
                    
                    # Slightly more futuristic transmission if available
                    if 'IOR' in node.inputs:
                        node.inputs['IOR'].default_value = 1.45
                    if 'Anisotropic' in node.inputs:
                        node.inputs['Anisotropic'].default_value = 0.25
                
                # If an emission shader exists, make it more neon-like
                if node.type == 'EMISSION':
                    if 'Color' in node.inputs:
                        node.inputs['Color'].default_value = (0.0, 0.95, 1.0, 1.0)
                    if 'Strength' in node.inputs:
                        node.inputs['Strength'].default_value = 3.0
                
                # Optional: enhance any glossy shader found
                if node.type == 'BSDF_GLOSSY':
                    if 'Color' in node.inputs:
                        node.inputs['Color'].default_value = (0.12, 0.18, 0.25, 1.0)
                    if 'Roughness' in node.inputs:
                        node.inputs['Roughness'].default_value = 0.08

            # If the material has no explicit emission node but uses Principled, keep it glossy/reflective
            mat.blend_method = 'OPAQUE'
            mat.shadow_method = 'OPAQUE'


# --- lighting code ---

# Cyberpunk lighting rework: lower neutral ambient and push neon pink/cyan contrast
bpy.data.worlds["World.001"].node_tree.nodes["HDRIHandler_ShaderNodeBackground"].inputs[1].default_value = 0.35

# Recolor and intensify the right-side area light to cyan for a strong key/fill
area_light.data.energy = 14.5
area_light.data.color = (0.0, 0.95, 1.0)

# Turn the back-wall light into a pink reflection source
area_light001.data.energy = 10.8
area_light001.data.color = (1.0, 0.08, 0.75)

# Make the left-side light a stronger neon pink rim/accent
area_light002.data.energy = 3.2
area_light002.data.color = (0.75, 0.85, 1.0)
area_light002.data.size = 0.28

# Push the top light slightly toward cool white/cyan for glossy highlights
area_light003.data.energy = 5.6
area_light003.data.color = (0.65, 0.9, 1.0)

# Add a dedicated cyan rim light from the back-right for bottle edge highlights
cyan_rim_data = bpy.data.lights.new('light', type="AREA")
cyan_rim = bpy.data.objects.new("CyanRim", cyan_rim_data)
cyan_rim.location = (0.62, 0.48, 0.42)
cyan_rim.scale = (0.45, 0.18, 0.45)
cyan_rim.rotation_euler = (1.25, 0.0, 2.55)
cyan_rim.data.energy = 10.0
cyan_rim.data.color = (0.0, 1.0, 1.0)
cyan_rim.data.shape = "SQUARE"
cyan_rim.data.size = 0.75
cyan_rim.data.shadow_soft_size = 2.0
bpy.context.collection.objects.link(cyan_rim)

# Add a dedicated pink accent light from the front-left for neon glow and reflections
pink_accent_data = bpy.data.lights.new('light', type="AREA")
pink_accent = bpy.data.objects.new("PinkAccent", pink_accent_data)
pink_accent.location = (-0.58, -0.18, 0.34)
pink_accent.scale = (0.38, 0.16, 0.38)
pink_accent.rotation_euler = (1.05, 0.0, -1.95)
pink_accent.data.energy = 9.5
pink_accent.data.color = (1.0, 0.05, 0.7)
pink_accent.data.shape = "SQUARE"
pink_accent.data.size = 0.7
pink_accent.data.shadow_soft_size = 2.0
bpy.context.collection.objects.link(pink_accent)

# Add a subtle point light for glowing accent on the bottle body
point_light.data.energy = 4.0
point_light.data.color = (0.0, 1.0, 0.95)
point_light.data.shadow_soft_size = 0.2

# --- background code ---

# --- Cyberpunk-inspired backdrop: dark gradient world with subtle neon accents ---
import bpy

world = bpy.data.worlds.get("World.001")
if world is not None:
    world.use_nodes = True
    nt = world.node_tree
    nodes = nt.nodes
    links = nt.links

    # Ensure a clean, controllable world setup
    bg = nodes.get("HDRIHandler_ShaderNodeBackground")
    if bg is None:
        bg = nodes.new(type="ShaderNodeBackground")
        bg.name = "HDRIHandler_ShaderNodeBackground"

    # Create a dark gradient using Texture Coordinate + Mapping + Gradient Texture + ColorRamp
    texcoord = nodes.get("Cyberpunk_TexCoord") or nodes.new(type="ShaderNodeTexCoord")
    texcoord.name = "Cyberpunk_TexCoord"

    mapping = nodes.get("Cyberpunk_Mapping") or nodes.new(type="ShaderNodeMapping")
    mapping.name = "Cyberpunk_Mapping"
    mapping.inputs[3].default_value = (0.0, 0.0, 0.0)
    mapping.inputs[2].default_value = (0.0, 0.0, 0.0)
    mapping.inputs[3].default_value = (0.0, 0.0, 0.0)
    mapping.inputs[2].default_value = (0.0, 0.0, 0.0)
    mapping.inputs[3].default_value = (0.0, 0.0, 0.0)

    grad = nodes.get("Cyberpunk_Gradient") or nodes.new(type="ShaderNodeTexGradient")
    grad.name = "Cyberpunk_Gradient"
    grad.gradient_type = 'LINEAR'

    ramp = nodes.get("Cyberpunk_ColorRamp") or nodes.new(type="ShaderNodeValToRGB")
    ramp.name = "Cyberpunk_ColorRamp"
    ramp.color_ramp.elements[0].position = 0.15
    ramp.color_ramp.elements[0].color = (0.01, 0.01, 0.02, 1.0)
    ramp.color_ramp.elements[1].position = 0.95
    ramp.color_ramp.elements[1].color = (0.03, 0.00, 0.06, 1.0)

    # Add a subtle neon tint layer by blending a second ramp into the background color
    neon_ramp = nodes.get("Cyberpunk_NeonRamp") or nodes.new(type="ShaderNodeValToRGB")
    neon_ramp.name = "Cyberpunk_NeonRamp"
    if len(neon_ramp.color_ramp.elements) < 2:
        neon_ramp.color_ramp.elements.new(0.5)
    neon_ramp.color_ramp.elements[0].position = 0.20
    neon_ramp.color_ramp.elements[0].color = (0.00, 0.85, 1.00, 1.0)  # cyan
    neon_ramp.color_ramp.elements[1].position = 0.80
    neon_ramp.color_ramp.elements[1].color = (1.00, 0.10, 0.75, 1.0)  # magenta

    mix = nodes.get("Cyberpunk_Mix") or nodes.new(type="ShaderNodeMixRGB")
    mix.name = "Cyberpunk_Mix"
    mix.blend_type = 'ADD'
    mix.inputs[0].default_value = 0.12

    # Clear existing links to the background node input if needed
    for l in list(links):
        if l.to_node == bg and l.to_socket == bg.inputs[0]:
            links.remove(l)

    # Rewire world nodes
    try:
        links.new(texcoord.outputs[0], mapping.inputs[0])
        links.new(mapping.outputs[0], grad.inputs[0])
        links.new(grad.outputs[0], ramp.inputs[0])
        links.new(ramp.outputs[0], mix.inputs[1])
        links.new(neon_ramp.outputs[0], mix.inputs[2])
        links.new(mix.outputs[0], bg.inputs[0])
    except Exception:
        pass

    # Keep the world dark, with only a hint of glow
    bg.inputs[1].default_value = 0.18

    # Optional: slightly blue-purple world color fallback if the node setup is bypassed
    world.color = (0.01, 0.01, 0.03)

# Optional: add a very subtle global tint to help the cyberpunk mood without overpowering the bottle
for light_name in ["Area", "Area.001", "Area.002", "Area.003", "Point"]:
    obj = bpy.data.objects.get(light_name)
    if obj and obj.type == 'LIGHT':
        # Keep existing lighting mostly intact; just nudge toward cooler neon tones
        if obj.name in {"Area.002", "Area.003"}:
            obj.data.color = (0.85, 0.95, 1.0)
        elif obj.name == "Point":
            obj.data.color = (0.7, 0.9, 1.0)
