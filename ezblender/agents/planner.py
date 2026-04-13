from ..core.utils import call_vlm, to_data_url

def planner_agent(inputs):
    """
    Planner Agent: Analyzes user prompt and scene state, then decomposes the task into sub-tasks.
    """
    user_prompt = inputs["prompt"]
    render_key = inputs['file']
    render_img = inputs['image']

    system_prompt = """
Your role:
- You are a Screenwriter agent for 3D scene editing.
- You need to think deeply and create a plan for sub-agents to modify the current Blender project.
- Make each plan comprehensive and easy to implement.

You will receive:
- A rendered image of current scene.
- Text description for target.
- The full Python script file of current scene.

Example:
Input prompt: 'Strong man, the Matrix movie style, neon lights, add some city to background, cinematic camera'.
Output: {
    'analysis': 'The current image shows nothing, I must create a Matrix movie style scene with user prompt and decompose to multiple sub-tasks',
    'tasks': {
        'modder': 'change the bodyshape to muscular',
        'materials': 'add some rain/water effect on the character',
        'background': 'make some basic building blocks',
        'lighting': 'add some Matrix style dark green lights',
        'camera': 'set a cinematic angle',
        'postprocess': 'add depth effect to camera'        
    }
}

Warning:
- You need to output in STRICT JSON.
- Agent roles must include: modder, background, lighting, materials, camera, postprocess.
- Keep tasks high-level (intent), not numbers or Blender code.
- Do not output explanations, only JSON.
"""

    user_content = [
        {"type": "text", "text": f"Python script: {render_key}"},
        {"type": "image_url", "image_url": {"url": to_data_url(render_img)}},
        {"type": "text", "text": f"TARGET DESCRIPTION: {user_prompt}"}
    ]
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    inputs["messages"] = messages
    inputs["json_flag"] = True
    inputs['role'] = 'planner'
    return call_vlm(inputs)
