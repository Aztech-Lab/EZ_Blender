import bpy

# Set all materials to a glowing neon red
for mat in bpy.data.materials:
    if mat.use_nodes:
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        # Add nodes
        node_emission = nodes.new(type='ShaderNodeEmission')
        node_emission.inputs[0].default_value = (1.0, 0.0, 0.0, 1.0) # Red
        node_emission.inputs[1].default_value = 10.0 # Glow
        
        node_output = nodes.new(type='ShaderNodeOutputMaterial')
        
        # Link
        mat.node_tree.links.new(node_emission.outputs[0], node_output.inputs[0])

# Reduce background light
if "World.001" in bpy.data.worlds:
    bpy.data.worlds["World.001"].node_tree.nodes["HDRIHandler_ShaderNodeBackground"].inputs[1].default_value = 0.1
