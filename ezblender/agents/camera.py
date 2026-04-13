from ..core.utils import call_vlm

def camera_agent(inputs):
    """
    Blender Camera Agent: Responsible for camera positioning and settings.
    """
    prompt = inputs["prompt"]
    render_key = inputs["file"]

    system_prompt = """You are the Blender Camera Agent.
You will receive:
- The Blender Python script file.
- A camera task goal.

Example for a new camera:
```python
import bpy
camera_data = bpy.data.cameras.new(name='CustomCamera')
camera_object = bpy.data.objects.new('CustomCamera', camera_data)
bpy.context.scene.collection.objects.link(camera_object)
camera_object.location = (0, -10, 5)
camera_object.rotation_euler = (1.1, 0, 0)
bpy.context.scene.camera = camera_object
```

Task:
- Suggest new Blender Python code that can be APPENDED to the script.
- Build a new camera named 'CustomCamera'.
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
    inputs['role'] = 'camera'
    return call_vlm(inputs)
