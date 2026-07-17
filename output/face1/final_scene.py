import bpy

""" Leave this comment block unchanged across edits.

Mouth open (ranges from 0 to 1): degree of mouth openness
Scrunch nose (range from 0 to 1): scrunching of the nose.
Pursed lips (range from 0 to 1): degree to which to corners of the mouth are close together.

Left side smile (range from -1 to 1): left corner of mouth moves up to form a smile. Negative values move the corner down, as if in a frown.
Right side smile (range from -1 to 1): right corner of mouth moves up to form a smile. Negative values move the corner down, as if in a frown.
Left eye close (range from -0.3 to 1): positive values narrows the left eye, negative values widens it.
Right eye close (range from -0.3 to 1): positive values narrows the right eye, negative values widens it.
Left raised eyebrow (range from 0 to 1): arches the left eyebrow, as in a skeptical look or angry.
Right raised eyebrow (range from 0 to 1): arches the right eyebrow, as in a skeptical look or angry.
Left lifted eyebrow (range from 0 to 1): Left raises the eyebrow, as in a surprised look.
Right lifted eyebrow (range from 0 to 1): Right raises the eyebrow, as in a surprised look.
Left furrow eyebrow (range from 0 to 1): furrows the left eyebrow, as in angry or concentrated.
Right furrow eyebrow (range from 0 to 1): furrows the right eyebrow, as in angry or concentrated.
Left eyebrow upward tilt (range from 0 to 1): tilts the left eyebrow outwards, as in a sad look.
Right eyebrow upward tilt (range from 0 to 1): tilts the right eyebrow outwards, as in a sad look.
Left eye outer corner lift (range from -1 to 1): positive values the outer corner of the right eye up, as in smiling with the eyes. negative values move the outer corner down, as in sad expression.S
Right eye outer corner lift (range from -1 to 1): positive values the outer corner of the right eye up, as in smiling with the eyes. negative values move the outer corner down, as in sad expression.
Left eye inner corner lift (range from 0 to 1): positive values move the inner corner up, useful  when the outer corner is down.
Right eye inner corner lift (range from 0 to 1): positive values move the inner corner up, useful  when the outer corner is down.
"""

bpy.data.shape_keys["Key"].key_blocks["Mouth open"].value = 0
bpy.data.shape_keys["Key"].key_blocks["Pursed lips"].value = 0.15
bpy.data.shape_keys["Key"].key_blocks["Scrunch nose"].value = 0.1

bpy.data.shape_keys["Key"].key_blocks["Left side smile"].value = -0.05
bpy.data.shape_keys["Key"].key_blocks["Right side smile"].value = -0.05
bpy.data.shape_keys["Key"].key_blocks["Left eye close"].value = 0.18
bpy.data.shape_keys["Key"].key_blocks["Right eye close"].value = 0.18
bpy.data.shape_keys["Key"].key_blocks["Left raised eyebrow"].value = 0.2
bpy.data.shape_keys["Key"].key_blocks["Right raised eyebrow"].value = 0.2
bpy.data.shape_keys["Key"].key_blocks["Left lifted eyebrow"].value = 0.05
bpy.data.shape_keys["Key"].key_blocks["Right lifted eyebrow"].value = 0.05
bpy.data.shape_keys["Key"].key_blocks["Left furrow eyebrow"].value = 0.35
bpy.data.shape_keys["Key"].key_blocks["Right furrow eyebrow"].value = 0.35
bpy.data.shape_keys["Key"].key_blocks["Left eyebrow upward tilt"].value = 0.1
bpy.data.shape_keys["Key"].key_blocks["Right eyebrow upward tilt"].value = 0.1
bpy.data.shape_keys["Key"].key_blocks["Left eye outer corner lift"].value = -0.15
bpy.data.shape_keys["Key"].key_blocks["Right eye outer corner lift"].value = -0.15
bpy.data.shape_keys["Key"].key_blocks["Left eye inner corner lift"].value = 0.08
bpy.data.shape_keys["Key"].key_blocks["Right eye inner corner lift"].value = 0.08




# --- AI AGENT MODIFICATIONS ---

# --- Start materials ---
try:
    for mat in bpy.data.materials:
        if mat.use_nodes:
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links

            mat_name = mat.name.lower()

            principled = None
            output = None
            emission = None

            for node in nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    principled = node
                elif node.type == 'OUTPUT_MATERIAL':
                    output = node
                elif node.type == 'EMISSION':
                    emission = node

            # Subtle glossy / reflective skin response
            if principled:
                if principled.inputs.get('Roughness'):
                    principled.inputs['Roughness'].default_value = max(0.18, min(principled.inputs['Roughness'].default_value, 0.35))
                if principled.inputs.get('Specular'):
                    principled.inputs['Specular'].default_value = max(principled.inputs['Specular'].default_value, 0.55)
                if principled.inputs.get('Clearcoat'):
                    principled.inputs['Clearcoat'].default_value = max(principled.inputs['Clearcoat'].default_value, 0.12)
                if principled.inputs.get('Clearcoat Roughness'):
                    principled.inputs['Clearcoat Roughness'].default_value = min(principled.inputs['Clearcoat Roughness'].default_value, 0.25)

            # Bright fluorescent emissive eyes / tattoo-like materials
            is_emissive_target = any(k in mat_name for k in ['eye', 'eyes', 'tattoo', 'tattoos', 'neon', 'cyber', 'cybernetic', 'glow'])
            if is_emissive_target:
                if emission is None:
                    emission = nodes.new(type='ShaderNodeEmission')
                    emission.location = (0, 0)

                # Neon cyan/magenta sci-fi palette
                if 'eye' in mat_name:
                    emission.inputs['Color'].default_value = (0.2, 0.95, 1.0, 1.0)
                    emission.inputs['Strength'].default_value = 25.0
                else:
                    emission.inputs['Color'].default_value = (1.0, 0.15, 0.9, 1.0)
                    emission.inputs['Strength'].default_value = 18.0

                # Ensure emission reaches material output
                if output:
                    # Prefer direct emission to surface for glowing materials
                    for link in list(links):
                        if link.to_node == output and link.to_socket.name == 'Surface':
                            links.remove(link)
                    links.new(emission.outputs['Emission'], output.inputs['Surface'])

                # If a Principled shader exists, make the material less dull
                if principled:
                    if principled.inputs.get('Roughness'):
                        principled.inputs['Roughness'].default_value = min(principled.inputs['Roughness'].default_value, 0.22)
                    if principled.inputs.get('Specular'):
                        principled.inputs['Specular'].default_value = max(principled.inputs['Specular'].default_value, 0.65)
except Exception as e:
    print(f'![Agent materials Error]: {e}')
# --- End materials ---


# --- Start lighting ---
try:

    # --- Cyberpunk neon lighting setup (append only) ---
    import bpy
    from mathutils import Vector

    scene = bpy.context.scene

    # Darken world slightly for stronger contrast
    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[1].default_value = 0.25

    # Helper to create lights
    def add_light(name, light_type, location, rotation, energy, color, size=1.5):
        light_data = bpy.data.lights.new(name=name, type=light_type)
        light_data.energy = energy
        light_data.color = color
        if light_type == 'AREA':
            light_data.shape = 'RECTANGLE'
            light_data.size = size
            light_data.size_y = size
        obj = bpy.data.objects.new(name, light_data)
        bpy.context.collection.objects.link(obj)
        obj.location = location
        obj.rotation_euler = rotation
        return obj

    # Soft neutral key light for facial readability
    add_light(
        name="Cyber_Key",
        light_type='AREA',
        location=(0.8, -1.2, 1.6),
        rotation=(1.15, 0.0, 0.55),
        energy=4.0,
        color=(1.0, 0.92, 0.85),
        size=2.2,
    )

    # Cyan rim light from one side/back
    add_light(
        name="Cyber_Rim_Cyan",
        light_type='AREA',
        location=(-1.8, 0.6, 1.5),
        rotation=(1.35, 0.0, -1.2),
        energy=10.0,
        color=(0.0, 1.0, 1.0),
        size=2.5,
    )

    # Magenta rim/accent light from opposite side/back
    add_light(
        name="Cyber_Rim_Magenta",
        light_type='AREA',
        location=(1.9, 0.8, 1.4),
        rotation=(1.25, 0.0, 1.15),
        energy=9.0,
        color=(1.0, 0.1, 0.8),
        size=2.5,
    )

    # Small front accent to make glowing facial elements stand out
    add_light(
        name="Cyber_Front_Accent",
        light_type='POINT',
        location=(0.0, -0.6, 1.35),
        rotation=(0.0, 0.0, 0.0),
        energy=2.5,
        color=(0.35, 0.8, 1.0),
    )
except Exception as e:
    print(f'![Agent lighting Error]: {e}')
# --- End lighting ---


# --- Start background ---
try:

    # --- Cyberpunk atmosphere background ---
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links

    # Clear existing nodes
    for node in list(nodes):
        nodes.remove(node)

    output_node = nodes.new(type="ShaderNodeOutputWorld")
    output_node.location = (400, 0)
    background_node = nodes.new(type="ShaderNodeBackground")
    background_node.location = (150, 0)
    background_node.inputs["Strength"].default_value = 0.25

    texcoord_node = nodes.new(type="ShaderNodeTexCoord")
    texcoord_node.location = (-700, 0)
    mapping_node = nodes.new(type="ShaderNodeMapping")
    mapping_node.location = (-500, 0)
    mapping_node.inputs["Rotation"].default_value[2] = 0.15

    gradient_node = nodes.new(type="ShaderNodeTexGradient")
    gradient_node.location = (-300, 0)
    gradient_node.gradient_type = 'LINEAR'

    ramp_node = nodes.new(type="ShaderNodeValToRGB")
    ramp_node.location = (-80, 0)
    ramp = ramp_node.color_ramp
    ramp.elements[0].position = 0.15
    ramp.elements[0].color = (0.01, 0.01, 0.03, 1.0)  # deep dark blue-black
    ramp.elements[1].position = 0.95
    ramp.elements[1].color = (0.02, 0.12, 0.18, 1.0)  # subtle cyan haze

    # Add a faint neon accent using a second ramp mixed in
    noise_node = nodes.new(type="ShaderNodeTexNoise")
    noise_node.location = (-300, -250)
    noise_node.inputs["Scale"].default_value = 2.5
    noise_node.inputs["Detail"].default_value = 4.0

    ramp2_node = nodes.new(type="ShaderNodeValToRGB")
    ramp2_node.location = (-80, -250)
    ramp2 = ramp2_node.color_ramp
    ramp2.elements[0].position = 0.35
    ramp2.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp2.elements[1].position = 0.85
    ramp2.elements[1].color = (0.55, 0.0, 0.75, 1.0)  # muted neon magenta

    mix_node = nodes.new(type="ShaderNodeMixRGB")
    mix_node.location = (80, -120)
    mix_node.blend_type = 'ADD'
    mix_node.inputs["Fac"].default_value = 0.12

    links.new(texcoord_node.outputs["Generated"], mapping_node.inputs["Vector"])
    links.new(mapping_node.outputs["Vector"], gradient_node.inputs["Vector"])
    links.new(gradient_node.outputs["Fac"], ramp_node.inputs["Fac"])
    links.new(noise_node.outputs["Fac"], ramp2_node.inputs["Fac"])
    links.new(ramp_node.outputs["Color"], mix_node.inputs[1])
    links.new(ramp2_node.outputs["Color"], mix_node.inputs[2])
    links.new(mix_node.outputs["Color"], background_node.inputs["Color"])
    links.new(background_node.outputs["Background"], output_node.inputs["Surface"])
except Exception as e:
    print(f'![Agent background Error]: {e}')
# --- End background ---
