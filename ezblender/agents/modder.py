from ..core.utils import call_vlm, to_data_url

def modder_agent(inputs):
    """
    Blender Model Agent: Responsible for geometry modifications.
    """
    prompt = inputs["prompt"]
    render_key = inputs["file"]
    render_img = inputs['image']

    system_prompt = """You are the Blender Modeling Expert Agent.
    Your goal is to modify object shapes, proportions, or mesh parameters (like shape keys) to match a visual description.

    You must follow a THREE-STEP reasoning process in your analysis:
    1) **Visual Difference**: Compare the current rendering with the target goal. Is the character too thin? Not muscular enough? Is the face not expressive enough?
    2) **Code Mapping**: Look at the provided Python script. Which specific variables (e.g., 'Abs', 'ChestEnlarge', 'BicepSize') or numerical values are responsible for the body/object shape? Identify the ones that need to change.
    3) **Code Implementation**: Provide the final code assignments.

    CRITICAL RULES:
    - Only suggest modifications for the variables that ALREADY EXIST in the script.
    - Do NOT create new variables or complex logic unless absolutely necessary.
    - Output ONLY the assignment lines (e.g., Abs = 1.0).
    - Output STRICT JSON with keys: {"analysis", "suggested_code"}.
    """

    user_content = [
        {"type": "text", "text": f"Python script: {render_key}"},
        {"type": "image_url", "image_url": {"url": to_data_url(render_img)}},
        {"type": "text", "text": f"TARGET GOAL: {prompt}"}
    ]
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    inputs["messages"] = messages
    inputs["json_flag"] = True
    inputs['role'] = 'modder'
    return call_vlm(inputs)

def modder_critic_agent(inputs):
    """
    Blender Model Refinement Agent: Evaluates the current model state and suggests refinements.
    """
    user_prompt = inputs['prompt']
    render_key = inputs['file']
    render_img = inputs['image']

    system_prompt = """You are a Blender model refinement agent.
You will receive:
- The Python scene file used to set parameters.
- A brief target description.

Task:
- Check rendered image to understand how well the last render matched the target.
- Give a satisfaction score (0.0 to 1.0, 0.5 is good enough).
- If not satisfactory, suggest new values for existing parameters in the script.
- Read the file for value setting and ranges.
- Output STRICT JSON with keys: {"score", "end_flag", "analysis", "suggested_code"}.
- Early stop (end_flag=True) if satisfied or no progress.
"""
    user_content = [
        {"type": "text", "text": f"Python script: {render_key}"},
        {"type": "image_url", "image_url": {"url": to_data_url(render_img)}},
        {"type": "text", "text": f"TARGET DESCRIPTION: {user_prompt}"},
    ]
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]
    inputs['messages'] = messages 
    inputs['json_flag'] = True
    inputs['role'] = 'modder_refine'
    return call_vlm(inputs)
