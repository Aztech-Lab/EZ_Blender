import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from .utils import get_key_from_file, code_to_file, apply_suggested_code, run_blender
from ..agents import (
    modder_agent, material_agent, lighting_agent, background_agent
)

def _call_single_agent(agent_name, task_desc, client, model, init_script, init_img):
    """Internal helper to dispatch to a specific agent."""
    print(f"[*] Starting {agent_name} Agent...")
    agent_inputs = {
        "client": client,
        "model": model,
        "prompt": task_desc,
        "file": get_key_from_file(init_script),
        "image": init_img
    }
    
    if agent_name == "modder":
        return agent_name, modder_agent(agent_inputs)
    elif agent_name == "materials":
        return agent_name, material_agent(agent_inputs)
    elif agent_name == "lighting":
        return agent_name, lighting_agent(agent_inputs)
    elif agent_name == "background":
        return agent_name, background_agent(agent_inputs)
    return None, None

def execute_sequential(tasks, client, model, init_script, init_img):
    """Executes agents one by one."""
    results = {}
    for name, desc in tasks.items():
        if not desc: continue
        res_name, res_val = _call_single_agent(name, desc, client, model, init_script, init_img)
        if res_name:
            results[res_name] = res_val
    return results

def execute_parallel(tasks, client, model, init_script, init_img):
    """Executes agents in parallel using threads."""
    results = {}
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(_call_single_agent, name, desc, client, model, init_script, init_img)
            for name, desc in tasks.items() if desc
        ]
        for future in futures:
            res_name, res_val = future.result()
            if res_name:
                results[res_name] = res_val
    return results

def assemble_final_script(init_script, results, out_dir, output_name="final_scene.py"):
    """Combines all agent codes into a single Python script with error isolation."""
    print("[*] Assembling final script with fault-tolerance...")
    final_script_path = os.path.join(out_dir, output_name)
    
    # 1. Start with the baseline script
    try:
        base_code = get_key_from_file(init_script)
    except Exception as e:
        print(f"❌ Error reading init_script: {e}")
        base_code = "# Error reading initial script"
        
    final_code_lines = [base_code, "\n# --- AI AGENT MODIFICATIONS ---"]
    
    # 2. Wrap each agent's contribution in a try-except block
    for name in ["materials", "lighting", "camera", "background"]:
        if name in results and results[name].get("suggested_code"):
            code = results[name]["suggested_code"]
            safe_block = f"\n# --- Start {name} ---\ntry:\n{_indent_code(code)}\nexcept Exception as e:\n    print(f'![Agent {name} Error]: {{e}}')\n# --- End {name} ---\n"
            final_code_lines.append(safe_block)
            
    combined_text = "\n".join(final_code_lines)
    
    # 3. Handle Modder replacement (handle it last on a temporary copy)
    if "modder" in results and results["modder"].get("suggested_code"):
        fd, tmp_path = tempfile.mkstemp(suffix=".py")
        os.close(fd)
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(combined_text)
        
        try:
            final_code = apply_suggested_code(results["modder"]["suggested_code"], tmp_path)
        except Exception as e:
            print(f"❌ Modder application failed: {e}")
            final_code = combined_text
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    else:
        final_code = combined_text
        
    # 4. Final Write
    with open(final_script_path, "w", encoding="utf-8") as f:
        f.write(final_code)
    
    print(f"[+] Final script saved to {final_script_path} ({len(final_code)} bytes)")
    return final_script_path

def _indent_code(code, spaces=4):
    """Helper to indent code for try-except blocks."""
    indent = " " * spaces
    return "\n".join([indent + line if line.strip() else line for line in code.splitlines()])

def run_final_render(blender_exe, scene_blend, script_path, render_script, out_dir, render_name="result_render.png"):
    """Executes the actual Blender render process."""
    result_img = os.path.join(out_dir, render_name)
    print(f"[*] Rendering result to: {result_img}")
    render_result = run_blender(blender_exe, scene_blend, script_path, render_script, result_img)
    return render_result, result_img
