from ..core.utils import call_vlm

def debug_agent(inputs):
    """
    Debug Agent: Identifies and fixes bugs in Blender Python scripts based on error logs.
    """
    system_prompt = """You are a Debug Agent for Blender Python scripts.
You will receive:
- Master prompt from user.
- A code snippet that caused Blender to crash.
- The Blender error log.

Task:
- Identify the bug in the code based on the error log.
- Fix ONLY the bug, align it with Master prompt if possible.
- Output STRICT JSON with keys: {"analysis", "suggested_code"}.
"""
    content = [
        {"type": "text", "text": f"Agent name: {inputs['name']}"},
        {"type": "text", "text": f"Original code:\n{inputs['code']}"},
        {"type": "text", "text": f"Error log:\n{inputs['error_log']}"},
        {"type": "text", "text": f"Master prompt:\n{inputs['master_prompt']}"}
    ]

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ]

    inputs["messages"] = messages
    inputs["json_flag"] = True
    inputs['role'] = 'debug'
    return call_vlm(inputs)
