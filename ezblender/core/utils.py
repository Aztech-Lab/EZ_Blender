import os
import shutil
import re
import base64
import json
import time
import tempfile
import subprocess
from pathlib import Path
from openai import OpenAI, AzureOpenAI

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def copy_script(src, dst):
    shutil.copyfile(src, dst)
    return dst

def make_numeric_dir(path="."):
    entries = os.listdir(path)
    numeric_dirs = []
    for entry in entries:
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path) and entry.isdigit():
            numeric_dirs.append(int(entry))

    if not numeric_dirs:
        next_dir = "0"
    else:
        next_dir = str(max(numeric_dirs) + 1)

    new_path = os.path.join(path, next_dir)
    os.makedirs(new_path, exist_ok=True)
    return new_path

def get_key_from_file(render_key):
    with open(render_key, "r", encoding="utf-8") as f:
        scene_code = f.read()
    return scene_code

def code_to_file(codex, base_file=None, out_file=None):
    if isinstance(codex, str):
        codex_text = codex
    else:
        codex_text = "\n\n".join(codex)

    script_parts = []
    if base_file:
        with open(base_file, "r", encoding="utf-8") as f:
            script_parts.append(f.read())
    script_parts.append(codex_text)

    full_script = "\n\n".join(script_parts)

    if out_file is None:
        fd, tmp_path = tempfile.mkstemp(suffix=".py", prefix="agent_scene_")
        os.close(fd)
        out_file = tmp_path

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(full_script)

    return out_file

def normalize_quotes(s: str) -> str:
    return s.replace("'", '"')

def apply_suggested_code(suggested_code, code_file):
    with open(code_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updates = {}
    if not isinstance(suggested_code, str):
        return ""
    for line in suggested_code.splitlines():
        if "=" in line:
            lhs, rhs = line.split("=", 1)
            updates[normalize_quotes(lhs.strip())] = rhs.strip()

    new_lines = []
    for line in lines:
        if "=" in line:
            indent = len(line) - len(line.lstrip(" "))
            lhs, _ = line.split("=", 1)
            norm_lhs = normalize_quotes(lhs.strip())
            if norm_lhs in updates:
                lhs_clean = lhs.strip()
                rhs_new = updates[norm_lhs]
                line = " " * indent + f"{lhs_clean} = {rhs_new}\n"
        new_lines.append(line)

    return "".join(new_lines)

def to_data_url(img_path: str) -> str:
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    ext = "png" if img_path.lower().endswith("png") else "jpeg"
    return f"data:image/{ext};base64,{b64}"

def decompose(full_content):
    try:
        # Try to find JSON within the content if it's not pure JSON
        json_match = re.search(r'\{.*\}', full_content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
        else:
            data = json.loads(full_content)
        data['type'] = 'json'
    except Exception:
        data = {"type": 'code', "data": full_content}
    return data

def call_vlm(inputs):
    client = inputs['client']
    model = inputs['model']
    messages = inputs['messages']
    json_flag = inputs.get('json_flag', False)
    role = inputs.get('role', 'Agent')
    
    print(f'----------------{role} Agent Thinking...')
    try:
        # Standardize parameter for newer models (o1, gpt-5 etc.)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.5,
            max_completion_tokens=3000,
            **({"response_format": {"type": "json_object"}} if json_flag else {})
        )
        content = response.choices[0].message.content
        data = decompose(content)
        data['usage'] = response.usage.dict()
        data['role'] = role
        print('----------------Thinking End.')
        return data
    except Exception as e:
        print(f"❌ VLM Call failed for {role}:", e)
        return {"analysis": f"error: {str(e)}", "role": role}

def run_blender(blender_cmd, blender_scene, render_key, render_setting, render_path, timeout=600):
    """
    Executes Blender in background mode to run a script and render an image.
    """
    print('-----------------------Start Rendering...')
    ensure_dir(os.path.dirname(render_path))
    command = [
        blender_cmd, "--background",
        os.path.abspath(blender_scene),
        "--python", os.path.abspath(render_setting),
        "--", os.path.abspath(render_key), os.path.abspath(render_path)
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            print(f"❌ Blender render failed:\n{result.stderr}")
        print('-----------------------Finish Rendering')
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'code': result.returncode, 
            'status': os.path.exists(render_path)
        }
    except Exception as e:
        print(f"❌ Blender execution error: {e}")
        return {'status': False, 'error': str(e)}

def init_client(api_key=None, endpoint=None, api_version="2024-12-01-preview"):
    """
    Initializes OpenAI or Azure OpenAI client.
    """
    key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")

    if not key:
        raise ValueError("API Key must be provided or set as environment variable.")

    if key.startswith("sk-"):
        # Standard OpenAI
        print("Using standard OpenAI client.")
        return OpenAI(api_key=key)
    else:
        # Azure OpenAI
        endp = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        if not endp:
            raise ValueError("Azure OpenAI Endpoint must be provided for Azure keys.")
        print(f"Using Azure OpenAI client at {endp}.")
        return AzureOpenAI(
            api_version=api_version,
            azure_endpoint=endp,
            api_key=key
        )
