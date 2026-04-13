from ..core.utils import call_vlm

def lighting_agent(inputs):
    """
    Blender Lighting Expert Agent: Responsible for adding/modifying lights.
    """
    prompt = inputs["prompt"]
    render_key = inputs["file"]

    system_prompt = """You are the Blender Lighting Expert Agent.
Your goal is to modify or add Blender lights to achieve a specific visual lighting setup.

You must follow a THREE-STEP reasoning process in your analysis:
1) **Visual Difference**: Compare the current rendering with the target lighting goal. Is it too dark? Too flat? Does it need specific rim lights or colored accent lights?
2) **Code Mapping**: Look at the provided Python script. Which existing light energy values, colors, or positions should change? Or do you need to add a new light object?
3) **Code Implementation**: Provide the final code.

CRITICAL LIGHTING RULES:
- KEEP ENERGY LOW: Ensure the 'energy' or 'strength' of each light is not overexposing the scene. Usually, keep individual light energy less than 15.0.
- HDR STRENGTH: If the background is too bright, you can adjust the World background strength.
- Suggest only the Python code that can be APPENDED to the existing script.
- Do NOT rewrite the entire script, only the changes or additions.
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
    inputs['role'] = 'lighting'
    return call_vlm(inputs)
