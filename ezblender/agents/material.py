from ..core.utils import call_vlm

def material_agent(inputs):
    """
    Blender Material Editing Agent: Handles material properties and shader modifications.
    """
    prompt = inputs["prompt"]
    render_key = inputs["file"]

    system_prompt = """You are the Blender Material Expert Agent.
    Your goal is to modify a Blender procedural material script to match a target visual description or image.

    You must follow a THREE-STEP reasoning process in your analysis:
    1) **Visual Difference**: Compare the current rendering with the target goal. What is the single most visually obvious difference? (e.g., base color, roughness, glow intensity, or texture scale).
    2) **Code Mapping**: Look at the provided Python script. Which variables or numerical values (like RGB colors, strengths, or scales) are most likely responsible for that visual difference?
    3) **Code Implementation**: Provide the final code. 

    CRITICAL CODE RULES:
    - ALWAYS use this loop for materials to ensure consistency:
    ```python
    for mat in bpy.data.materials:
    if mat.use_nodes:
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        # YOUR CODE HERE - use 'mat' variable!
    ```
    - If you're adding an Emission shader for a 'glowing' effect, make sure to connect it correctly to the 'Material Output' node.
    - Suggest only the Python code that can be APPENDED to the existing script.
    - Output STRICT JSON with keys: {"analysis", "suggested_code"}.
    """

    user_content = [
        {"type": "text", "text": f"Python script: {render_key}"},
        {"type": "text", "text": f"TARGET GOAL: {prompt}"}
    ]
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    inputs["messages"] = messages
    inputs["json_flag"] = True
    inputs['role'] = 'materials'
    return call_vlm(inputs)
