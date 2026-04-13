import os
from ezblender import init_client, debug_agent, get_key_from_file

with open("./creds/openai.txt", "r") as f:
    key = f.read().strip()
client = init_client(api_key=key)

error_log = "'material' is not defined"
original_code = """
for mat in bpy.data.materials:
    if mat.use_nodes:
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        emission_node = nodes.new(type='ShaderNodeEmission')
        emission_node.inputs['Strength'].default_value = 10.0
        material_output = nodes.get('Material Output')
        links.new(emission_node.outputs['Emission'], material_output.inputs['Surface'])
"""

debug_inputs = {
    "client": client,
    "model": "gpt-4o",
    "name": "materials",
    "code": original_code,
    "error_log": error_log,
    "master_prompt": "Make the object pure glowing neon red"
}

reply = debug_agent(debug_inputs)
print("DEBUG ANALYSIS:", reply['analysis'])
print("FIXED CODE:\n", reply['suggested_code'])
