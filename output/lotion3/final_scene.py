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
area_light.location =  (0.7558, -0.2978, 0.2950 ) # (x,y, z)
area_light.scale = (0.4320, 0.1758, 0.4320) # (scale_x, scale_y, scale_z)
area_light.rotation_euler = (0.7196, 1.5708, 0) # (radians_x, radians_y, radians_z)
area_light.data.energy = 14.0
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
area_light001.data.energy = 13.5
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
area_light002.data.energy = 1.8
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
area_light003.data.energy = 9.8
area_light003.data.color =  (1.0, 1.0, 1.0) # (R, G, B )
area_light003.data.shape = "SQUARE"
area_light003.data.size = 1.0
area_light003.data.shadow_soft_size = 3.14
bpy.context.collection.objects.link(area_light003)

# Point light 1: Slightly behind the lotion.
point_light_data =  bpy.data.lights.new('light', type="POINT")
point_light = bpy.data.objects.new("Point",  point_light_data)
point_light.location = (0.0071, 0.1756, 0.4689) 
point_light.data.energy = 3.2
point_light.data.color = (1.0, 1.0, 1.0)
point_light.data.shadow_soft_size = 0.0
bpy.context.collection.objects.link(point_light)


# --- AI AGENT MODIFICATIONS ---

# --- Start materials ---
try:
    import bpy

    for mat in bpy.data.materials:
        if mat.use_nodes:
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            principled = None
            output = None
            emission = None
            mix_shader = None

            for node in nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    principled = node
                elif node.type == 'OUTPUT_MATERIAL':
                    output = node

            if principled is not None:
                # Make the surface more glossy, reflective, and slightly metallic
                if 'Roughness' in principled.inputs:
                    principled.inputs['Roughness'].default_value = max(0.06, principled.inputs['Roughness'].default_value * 0.35)
                if 'Metallic' in principled.inputs:
                    principled.inputs['Metallic'].default_value = min(0.35, max(principled.inputs['Metallic'].default_value, 0.18))
                if 'Specular' in principled.inputs:
                    principled.inputs['Specular'].default_value = min(0.85, max(principled.inputs['Specular'].default_value, 0.65))
                if 'Clearcoat' in principled.inputs:
                    principled.inputs['Clearcoat'].default_value = min(1.0, max(principled.inputs['Clearcoat'].default_value, 0.75))
                if 'Clearcoat Roughness' in principled.inputs:
                    principled.inputs['Clearcoat Roughness'].default_value = min(0.12, max(principled.inputs['Clearcoat Roughness'].default_value, 0.03))
                if 'IOR' in principled.inputs:
                    principled.inputs['IOR'].default_value = 1.45

                # Push base color toward a sleek tech-style neutral tone if it is very dull
                if 'Base Color' in principled.inputs:
                    bc = principled.inputs['Base Color'].default_value
                    principled.inputs['Base Color'].default_value = (max(bc[0], 0.12), max(bc[1], 0.13), max(bc[2], 0.16), bc[3] if len(bc) > 3 else 1.0)

            # Add subtle neon emissive accents for a futuristic premium finish
            if output is not None:
                # Find existing links to Surface
                surface_links = [l for l in links if l.to_node == output and l.to_socket.name == 'Surface']
                original_surface = surface_links[0].from_socket if surface_links else None

                if original_surface is not None:
                    # Create emission and mix shader if not already present
                    emission = nodes.get('Neon_Emission')
                    if emission is None:
                        emission = nodes.new(type='ShaderNodeEmission')
                        emission.name = 'Neon_Emission'
                        emission.label = 'Neon_Emission'
                        emission.location = (output.location.x - 350, output.location.y - 120)
                        emission.inputs['Color'].default_value = (0.10, 0.95, 1.0, 1.0)
                        emission.inputs['Strength'].default_value = 0.35

                    mix_shader = nodes.get('Neon_Mix')
                    if mix_shader is None:
                        mix_shader = nodes.new(type='ShaderNodeMixShader')
                        mix_shader.name = 'Neon_Mix'
                        mix_shader.label = 'Neon_Mix'
                        mix_shader.location = (output.location.x - 120, output.location.y)

                    # Rewire surface through mix shader
                    for l in list(surface_links):
                        links.remove(l)
                    links.new(original_surface, mix_shader.inputs[1])
                    links.new(emission.outputs['Emission'], mix_shader.inputs[2])
                    mix_shader.inputs[0].default_value = 0.88
                    links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])

                    # If the material has a transmission-like look, keep it premium by slightly increasing emission tint contrast
                    if emission is not None:
                        emission.inputs['Color'].default_value = (0.0, 0.85, 1.0, 1.0)
                        emission.inputs['Strength'].default_value = 0.22
except Exception as e:
    print(f"![Agent materials Error]: {e}")
# --- End materials ---


# --- Start lighting ---
try:
    # Cyberpunk neon adjustment: reduce ambient HDR influence
    bpy.data.worlds["World.001"].node_tree.nodes["HDRIHandler_ShaderNodeBackground"].inputs[1].default_value = 0.75

    # Recolor and intensify the right-side key light to cyan
    area_light.data.energy = 14.0
    area_light.data.color = (0.0, 1.0, 1.0)

    # Back wall light becomes a strong pink fill/accent
    area_light001.data.energy = 13.5
    area_light001.data.color = (1.0, 0.0, 0.85)

    # Left side light becomes a pink rim accent, slightly stronger for contrast
    area_light002.data.energy = 1.8
    area_light002.data.color = (1.0, 0.15, 0.75)

    # Top light becomes cyan to create a cool overhead glow and sharper highlights
    area_light003.data.energy = 9.8
    area_light003.data.color = (0.1, 0.9, 1.0)

    # Point light becomes a bright pink highlight source behind the subject
    point_light.data.energy = 3.2
    point_light.data.color = (1.0, 0.1, 0.8)
except Exception as e:
    print(f"![Agent lighting Error]: {e}")
# --- End lighting ---


# --- Start background ---
try:

    # Cyberpunk backdrop adjustment: dark urban tone with neon-leaning world color
    world = bpy.data.worlds.get("World.001")
    if world is not None:
        world.use_nodes = True
        bg_nodes = world.node_tree.nodes
        bg_links = world.node_tree.links

        # Try to find the background node used by the current setup
        bg_node = bg_nodes.get("HDRIHandler_ShaderNodeBackground")
        if bg_node is None:
            bg_node = next((n for n in bg_nodes if n.type == 'BACKGROUND'), None)

        if bg_node is not None:
            # Darken the environment and tint it toward cyberpunk blue/purple
            bg_node.inputs[1].default_value = 0.18
            bg_node.inputs[0].default_value = (0.03, 0.04, 0.08, 1.0)
except Exception as e:
    print(f"![Agent background Error]: {e}")
# --- End background ---
