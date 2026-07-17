import bpy

# All values range from 0 (min) to 1 (max)
# preserve this comment in all further edits.

bpy.data.shape_keys["Key"].key_blocks["BellySag"].value = 0
bpy.data.shape_keys["Key"].key_blocks["BellyShrink"].value = 0
bpy.data.shape_keys["Key"].key_blocks["ShoulderWideness"].value = 0.2
bpy.data.shape_keys["Key"].key_blocks["BackTaper"].value = 0.15
bpy.data.shape_keys["Key"].key_blocks["ChestEnlarge"].value = 0.1
bpy.data.shape_keys["Key"].key_blocks["ChestArea"].value = 0.15
bpy.data.shape_keys["Key"].key_blocks["MoreChin"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Abs"].value = 0


# --- materials code ---

for mat in bpy.data.materials:
    if mat.use_nodes:
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        # YOUR CODE HERE - use 'mat' variable!

        principled_nodes = [n for n in nodes if n.type == 'BSDF_PRINCIPLED']
        output_nodes = [n for n in nodes if n.type == 'OUTPUT_MATERIAL']

        for bsdf in principled_nodes:
            # Metallic / chrome / synthetic polymer look
            if 'Base Color' in bsdf.inputs:
                bsdf.inputs['Base Color'].default_value = (0.55, 0.58, 0.62, 1.0)
            if 'Metallic' in bsdf.inputs:
                bsdf.inputs['Metallic'].default_value = 0.85
            if 'Roughness' in bsdf.inputs:
                bsdf.inputs['Roughness'].default_value = 0.22
            if 'Specular' in bsdf.inputs:
                bsdf.inputs['Specular'].default_value = 0.75
            if 'Clearcoat' in bsdf.inputs:
                bsdf.inputs['Clearcoat'].default_value = 0.35
            if 'Clearcoat Roughness' in bsdf.inputs:
                bsdf.inputs['Clearcoat Roughness'].default_value = 0.08
            if 'Subsurface' in bsdf.inputs:
                bsdf.inputs['Subsurface'].default_value = 0.0

        # Add a subtle neon glow to make the material feel cybernetic
        if output_nodes:
            output = output_nodes[0]
            surface_input = output.inputs.get('Surface')
            if surface_input is not None:
                # Find existing emission or create one
                emission = None
                for n in nodes:
                    if n.type == 'EMISSION':
                        emission = n
                        break
                if emission is None:
                    emission = nodes.new('ShaderNodeEmission')
                    emission.location = (-200, 0)
                    emission.inputs['Color'].default_value = (0.0, 1.0, 0.9, 1.0)
                    emission.inputs['Strength'].default_value = 1.5

                mix = None
                for n in nodes:
                    if n.type == 'MIX_SHADER':
                        mix = n
                        break
                if mix is None:
                    mix = nodes.new('ShaderNodeMixShader')
                    mix.location = (100, 0)
                    mix.inputs['Fac'].default_value = 0.08

                # Rewire if not already connected through a mix shader
                # Keep the existing shader as one input, emission as the other
                if not mix.inputs[1].links:
                    for link in list(links):
                        if link.to_node == output and link.to_socket == surface_input:
                            links.remove(link)
                    if principled_nodes:
                        links.new(principled_nodes[0].outputs['BSDF'], mix.inputs[1])
                    links.new(emission.outputs['Emission'], mix.inputs[2])
                    links.new(mix.outputs['Shader'], surface_input)

                # Neon circuit color
                emission.inputs['Color'].default_value = (0.0, 1.0, 0.85, 1.0)
                emission.inputs['Strength'].default_value = 2.5


# --- lighting code ---


# Cyberpunk lighting setup: add colored rim and accent lights
scene = bpy.context.scene

# Optional: darken world for stronger neon contrast
if scene.world is None:
    scene.world = bpy.data.worlds.new("World")
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[1].default_value = 0.15

# Remove existing lights only if you want a clean lighting reset
# for obj in [o for o in bpy.data.objects if o.type == 'LIGHT']:
#     bpy.data.objects.remove(obj, do_unlink=True)

# Cyan rim light
light_data = bpy.data.lights.new(name="CyberCyanRim", type='AREA')
light_data.energy = 8.0
light_data.color = (0.0, 0.9, 1.0)
light_data.shape = 'RECTANGLE'
light_data.size = 4.0
light_data.size_y = 2.0
light_obj = bpy.data.objects.new(name="CyberCyanRim", object_data=light_data)
light_obj.location = (2.5, -3.5, 2.0)
light_obj.rotation_euler = (1.2, 0.0, 0.8)
bpy.context.collection.objects.link(light_obj)

# Magenta rim light
light_data = bpy.data.lights.new(name="CyberMagentaRim", type='AREA')
light_data.energy = 7.0
light_data.color = (1.0, 0.1, 0.8)
light_data.shape = 'RECTANGLE'
light_data.size = 4.5
light_data.size_y = 2.2
light_obj = bpy.data.objects.new(name="CyberMagentaRim", object_data=light_data)
light_obj.location = (-2.8, -2.8, 1.8)
light_obj.rotation_euler = (1.1, 0.0, -0.9)
bpy.context.collection.objects.link(light_obj)

# Cool front fill to preserve detail without flattening
light_data = bpy.data.lights.new(name="CyberCoolFill", type='AREA')
light_data.energy = 3.5
light_data.color = (0.35, 0.55, 1.0)
light_data.shape = 'RECTANGLE'
light_data.size = 5.0
light_data.size_y = 5.0
light_obj = bpy.data.objects.new(name="CyberCoolFill", object_data=light_data)
light_obj.location = (0.0, 3.5, 2.2)
light_obj.rotation_euler = (1.55, 0.0, 3.14)
bpy.context.collection.objects.link(light_obj)

# Warm accent to contrast against cool tones
light_data = bpy.data.lights.new(name="CyberWarmAccent", type='POINT')
light_data.energy = 4.0
light_data.color = (1.0, 0.45, 0.15)
light_obj = bpy.data.objects.new(name="CyberWarmAccent", object_data=light_data)
light_obj.location = (-1.5, 1.5, 1.2)
bpy.context.collection.objects.link(light_obj)


# --- background code ---


# Set a futuristic cyberpunk-style world background
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world

world.use_nodes = True
nodes = world.node_tree.nodes
bg = nodes.get("Background")
if bg is None:
    bg = nodes.new(type="ShaderNodeBackground")

# Deep cyberpunk tone: dark blue-purple with subtle neon feel
bg.inputs[0].default_value = (0.03, 0.05, 0.10, 1.0)
bg.inputs[1].default_value = 0.8
