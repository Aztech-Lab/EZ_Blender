from ..core.utils import call_vlm

def background_agent(inputs):
    """
    Blender Background Design Agent: Responsible for world/environment settings.
    """
    prompt = inputs["prompt"]
    render_key = inputs["file"]

    system_prompt = """You are the Blender Background Agent.
You will receive:
- The Blender Python script file.
- A background task goal.

Task:
- Suggest new Blender Python code that can be APPENDED to the script.
- Quick way: change world color and brightness.
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
    inputs['role'] = 'background'
    return call_vlm(inputs)
